# IPTV-TVBox 自用项目

这是一个基于 `iptv-api` 优化的个人 IPTV 直播源与点播源管理平台。

## ✨ 核心功能

*   **📺 直播源聚合 (Live)**
    *   **自动测速**: 定时获取并测速验证，过滤无效源。
    *   **多源支持**: 集成 GitHub 优质源（Migu、China-TV-Live、BRTV 等）。
    *   **组播优化**: 包含全国各省市电信/联通/移动组播源配置，支持 RTP 转 HTTP/M3U。
    *   **EPG 支持**: 自动生成节目单信息。
    *   **自定义频道**: 通过 `config/demo.txt` 灵活配置频道列表。
    *   **订阅源体检**: 手动运行工作流生成检测报告，保守剔除无效链接，并支持按 IPv4/IPv6 分类导出结果。

*   **🎬 点播源集成 (VOD)**
    *   **优质接口**: 集成 `qist/tvbox` 等大神维护的高质量点播配置（饭太硬、FongMi、OK影视等）。
    *   **一键配置**: 提供 `source.json` 文件，直接导入 TVBox 即可使用。

*   **🚀 部署支持**
    *   **GitHub Actions**: 自动化构建与部署。
    *   **Docker**: 支持一键部署到 GHCR (GitHub Container Registry) 或本地运行。

## 📂 快速上手

### 1. 获取直播源结果
程序运行后（或 GitHub Actions 自动运行后），结果文件位于 `output/` 目录：
*   **M3U 格式**: `output/result.m3u` (推荐，含图标和 EPG)
*   **TXT 格式**: `output/result.txt` (适用于旧版播放器)

**引用地址 (示例)**:
```
https://raw.githubusercontent.com/<你的用户名>/iptv-tvbox/master/output/result.m3u
```

### 2. 配置 TVBox 点播源
在 TVBox 客户端设置中，使用以下地址作为数据源：
```
https://raw.githubusercontent.com/<你的用户名>/iptv-tvbox/master/source.json
```
该文件已内置了多个高质量的点播接口，支持自动更新。

### 3. 订阅源体检（可选）
在 GitHub Actions 中手动运行 `Check subscribe urls`，会输出订阅源检测报告，保守清理无效链接，并生成 `output/subscribe/ipv4.txt` 和 `output/subscribe/ipv6.txt` 分类结果。

## ⚙️ 配置文件说明

所有核心配置位于 `config/` 目录：

| 文件名 | 说明 |
| :--- | :--- |
| **config.ini** | 核心配置文件（测速参数、过滤规则、功能开关等） |
| **subscribe.txt** | 直播订阅源列表（已集成 Migu、央视、卫视等优质源） |
| **demo.txt** | 频道分类与排序模板（决定最终结果的频道顺序） |
| **epg.txt** | EPG 节目单来源列表（可插拔按需维护） |
| **rtp/** | 各省市组播源列表（用于组播转单播场景） |

## 🛠️ 本地运行与开发

### 环境要求
*   Python 3.13+
*   FFmpeg (可选，用于分辨率检测和 RTMP 推流)

### 安装与运行
```bash
# 安装依赖
pip install pipenv
pipenv install --dev

# 启动更新与测速
pipenv run dev

# 启动 Web 服务 (可选)
pipenv run service
```

### 🐳 Docker 部署指南

本项目支持多种 Docker 部署方式，您可以选择使用 GitHub 自动构建的镜像 (GHCR)，也可以在本地手动构建。

#### 1. 使用 GitHub 容器镜像 (推荐)

如果您已经 Fork 本项目并启用了 GitHub Actions，镜像会自动构建并发布到您的 GitHub Packages (GHCR)。

**前提条件**：
1. 确保您的机器已安装 Docker。
2. 将 `<你的GitHub用户名>` 替换为您的实际 GitHub 用户名（小写）。

**运行命令**：
```bash
# 1. 拉取最新镜像
docker pull ghcr.io/<你的GitHub用户名>/iptv-tvbox:latest

# 2. 启动容器
docker run -d \
  --name iptv-tvbox \
  --restart unless-stopped \
  -p 51888:51888 \
  -v $(pwd)/config:/iptv-api/config \
  -v $(pwd)/output:/iptv-api/output \
  -e TZ=Asia/Shanghai \
  ghcr.io/<你的GitHub用户名>/iptv-tvbox:latest
```

**参数说明**：
*   `-p 51888:51888`: 映射服务端口，启动后访问 `http://localhost:51888`。
*   `-v $(pwd)/config:/iptv-api/config`: **关键配置**，挂载本地 `config` 目录到容器，方便随时修改配置（如 `config.ini`, `subscribe.txt`）。
*   `-v $(pwd)/output:/iptv-api/output`: **结果持久化**，挂载 `output` 目录，确保生成的 M3U/TXT 文件保存在本地。
*   `-e TZ=Asia/Shanghai`: 设置容器时区，确保定时任务时间正确。

#### 2. 本地构建与运行

如果您修改了源码或需要自定义构建环境，可以使用此方法。

**构建镜像**：
```bash
# 在项目根目录下执行
docker build -t iptv-tvbox-local .
```

**运行容器**：
```bash
docker run -d \
  --name iptv-tvbox-local \
  -p 51888:51888 \
  -v $(pwd)/config:/iptv-api/config \
  -v $(pwd)/output:/iptv-api/output \
  -e TZ=Asia/Shanghai \
  iptv-tvbox-local
```

#### 3. 使用 Docker Compose (更方便的管理方式)

如果您不想每次都输入长命令，可以在项目根目录创建一个 `docker-compose.yml` 文件：

```yaml
version: '3.8'
services:
  iptv-tvbox:
    # 方式一：使用远程镜像
    image: ghcr.io/<你的GitHub用户名>/iptv-tvbox:latest
    # 方式二：使用本地构建 (取消注释下一行)
    # build: .
    container_name: iptv-tvbox
    restart: unless-stopped
    ports:
      - "51888:51888"
    volumes:
      - ./config:/iptv-api/config
      - ./output:/iptv-api/output
    environment:
      - TZ=Asia/Shanghai
```

**启动服务**：
```bash
docker-compose up -d
```

**查看日志**：
```bash
docker-compose logs -f
```

#### 4. 常见问题
*   **权限问题**：如果遇到 `Permission denied`，请尝试在命令前加 `sudo` (Linux/macOS)。
*   **Windows 用户**：请确保 Docker Desktop 已启动，并将路径中的 `$(pwd)` 替换为绝对路径 (例如 `D:\iptv-tvbox\config`)，或者在 PowerShell 中使用 `${PWD}`。

## 🔗 相关项目参考

*   **[iptv-checker](https://github.com/zhimin-dev/iptv-checker)**: 专注于 IPTV 播放列表的有效性检测，提供 Docker 和桌面端工具，支持后台定时检查与可视化管理。本项目借用了其“定期体检”的思路，通过 GitHub Actions 实现轻量级的订阅源自动化清洗。
*   **[webgrabplus-siteinipack](https://github.com/SilentButeo2/webgrabplus-siteinipack)**: 官方维护的 WebGrab+Plus 抓取配置包，包含全球大量 EPG 源站点的抓取规则。本项目目前的 EPG 采用整合好的 XML 接口，若有更深度的自定义抓取需求，可参考该项目的配置规则进行扩展。
    > **新增功能**: 本项目已集成 `Generate Custom EPG` 工作流，利用 WebGrab+Plus 和该项目的 siteini 规则，支持自定义生成 EPG (默认演示抓取 CCTV-1)。配置文件位于 `config/webgrabplus/`。

## ⚠️ 免责声明
本项目仅供学习交流使用，所有数据源均来自互联网公开渠道，不存储任何视频文件。请勿用于商业用途。
