# IPTV-TVBox

**一站式 IPTV 直播源与点播源管理平台**

> 🚀 **最佳拍档**: 本项目与 [MoonTVPlus](https://github.com/mtvpls/MoonTVPlus) 深度集成，打造“后端自动管理 + 前端极速播放”的家庭影音中心。

## ✨ 项目价值

- **后端自动化**: 定时抓取优质源，自动去重、测速、验证，持续输出稳定列表
- **前端体验**: Web 端即开即用，适配多终端，观影体验接近原生播放器
- **标准接口**: 输出 M3U/JSON/EPG，便于任意播放器或前端接入

## 🎯 功能概览

### 🛠️ 后端能力 (IPTV-TVBox)
- **全自动聚合**: GitHub 优质源 + 运营商组播源自动整合
- **智能生成**:
  - **直播**: 自动生成带 EPG 和台标的 M3U
  - **点播**: 自动生成 TVBox 专用 `source.json`
- **IPv4/IPv6 双栈**: 自动生成对应清单
- **开放 API**: 统一 HTTP 接口，支持任何兼容 M3U/JSON 的播放器

### 📺 前端能力 (MoonTVPlus)
- **多源聚合搜索**: 一次搜索返回全源结果
- **丰富详情页**: 剧集、演员、年份、简介完整展示
- **流畅在线播放**: HLS.js + ArtPlayer 组合
- **收藏与进度同步**: 支持多端同步播放进度
- **PWA 与响应式**: 移动端和桌面端自适应
- **外部播放器跳转**: PotPlayer、VLC、MPV、MX Player、nPlayer、IINA 等
- **视频超分**: Anime4K WebGPU 实时增强
- **弹幕系统**: 搜索、匹配、加载与屏蔽
- **评论抓取**: 豆瓣短评分页展示
- **自定义去广告**: 可扩展过滤逻辑
- **观影室**: 多人同步观影与互动（实验性）
- **M3U8 完整下载**: 合并切片输出完整视频
- **服务器离线下载**: 断点续传，提前缓存秒开
- **私人影库**: 支持 OpenList 或 Emby 接入

## 🧱 架构与流程

- IPTV-TVBox 定时聚合源并生成 M3U/JSON/EPG
- MoonTVPlus 订阅接口后提供搜索、播放、互动等前端能力
- 观影进度与收藏通过存储服务持久化

## 🚀 极速部署 (Docker Compose)

我们准备了开箱即用的组合部署方案，一键启动完整生态。

### 1. 启动服务

```bash
# 1. 下载项目
git clone https://github.com/<你的GitHub用户名>/iptv-tvbox.git
cd iptv-tvbox

# 2. 启动服务 (默认使用 GitHub 预构建镜像)
# 注意：如果是本地部署，建议设置环境变量 GITHUB_ACTOR=<你的GitHub用户名>
docker-compose up -d
```

> 💡 **提示**: 默认会启动 `iptv-tvbox` (后端)、`moontvplus` (前端) 和 `redis` (存储) 三个容器。

### 2. 服务访问

| 服务 | 地址 | 默认账号 | 说明 |
| :--- | :--- | :--- | :--- |
| **播放器 (前端)** | `http://localhost:3000` | `admin` / `admin` | 日常观影入口 |
| **管理后台** | `http://localhost:51888` | 无需账号 | 数据接口与日志 |

### 3. 存储建议（关键）

- **Kvrocks（推荐）**: 兼容 Redis 协议，持久化更稳，适合收藏与播放进度
- **Redis（可用但有风险）**: 未开启持久化或内存淘汰时可能丢数据

如需切换存储，仅需保证 MoonTVPlus 的 `NEXT_PUBLIC_STORAGE_TYPE` 与 `REDIS_URL` 指向对应实例即可。Kvrocks 与 Redis 通常可复用同一连接参数。

### 4. Docker 部署数据库说明

- **默认行为**: `docker-compose.yml` 已包含 `moontv-redis` 容器并挂载 `moontv-data` 卷，实现基础持久化
- **使用 Kvrocks**: 将 `moontv-redis` 替换为 Kvrocks 镜像，并将 `REDIS_URL` 指向 Kvrocks 容器
- **保留 Redis**: 如需更高可靠性，建议开启 AOF 或 RDB 持久化并为数据卷设置备份策略
- **远程存储**: `REDIS_URL` 可指向局域网或云端实例，便于多设备共享观看进度
 - **Kvrocks 挂载目录**: 建议挂载到 `/var/lib/kvrocks`，便于数据持久化与版本兼容

#### Kvrocks docker-compose 示例

```yaml
services:
  moontv-core:
    image: ghcr.io/mtvpls/moontvplus:latest
    container_name: moontv-core
    restart: on-failure
    ports:
      - "3000:3000"
    environment:
      - USERNAME=admin
      - PASSWORD=admin_password
      - NEXT_PUBLIC_STORAGE_TYPE=kvrocks
      - KVROCKS_URL=redis://moontv-kvrocks:6666
    networks:
      - moontv-network
    depends_on:
      - moontv-kvrocks
  moontv-kvrocks:
    image: apache/kvrocks
    container_name: moontv-kvrocks
    restart: unless-stopped
    volumes:
      - kvrocks-data:/var/lib/kvrocks
    networks:
      - moontv-network

networks:
  moontv-network:
    driver: bridge

volumes:
  kvrocks-data:
```

## 🔌 配置指南：连接前后端

首次启动 MoonTVPlus 后，需要完成以下订阅配置：

1. 打开浏览器访问 `http://localhost:3000` (或局域网 IP)
2. 登录 `admin/admin`
3. 进入 **设置 (Settings)** -> **订阅管理 (Subscription)**
4. 添加以下订阅源

### 📺 直播源 (Live TV)
- **名称**: `IPTV-TVBox` (或任意名称)
- **类型**: `M3U`
- **地址**: `http://<本机局域网IP>:51888/m3u`
  - 仅需 IPv6 频道时使用 `/ipv6/m3u`

### 🎬 点播源 (VOD)
- **名称**: `TVBox VOD`
- **类型**: `TVBox (JSON)`
- **地址**: `http://<本机局域网IP>:51888/source.json`

### 📅 电子节目单 (EPG)
- **地址**: `http://<本机局域网IP>:51888/epg/epg.xml`

> ⚠️ **重要提示**: 在 Docker 环境中，`localhost` 指向容器自身，因此必须填写宿主机局域网 IP（如 `192.168.1.5`），不要使用 `127.0.0.1`。

## 📂 进阶配置与自定义

所有核心配置位于 `config/` 目录，修改后重启容器即可生效。

### 1. 频道管理 (`config/`)
- `demo.txt`: 频道分类与排序模板
- `subscribe.txt`: 直播订阅源列表
- `blacklist.txt`: 黑名单

### 2. 参数调整 (`config/config.ini`)
- `open_update`: 是否开启自动更新
- `urls_limit`: 每个频道保留的源数量
- `ipv6_support`: 是否优先检测 IPv6 源

### 3. Logo 与 EPG
- **Logo**: 图片放入 `config/logo/`，文件名需与频道名一致
- **EPG**: 文件输出在 `output/epg/epg.xml`

## 🛠️ 其他部署方式

### 纯 Docker 部署 (仅后台)

如果仅作为源管理工具使用：

```bash
docker run -d \
  --name iptv-tvbox \
  --restart unless-stopped \
  -p 51888:51888 \
  -v $(pwd)/config:/iptv-api/config \
  -v $(pwd)/output:/iptv-api/output \
  -v $(pwd)/source.json:/iptv-api/source.json \
  -e TZ=Asia/Shanghai \
  ghcr.io/<你的GitHub用户名>/iptv-tvbox:latest
```

- **端口映射**: `51888:51888`
- **配置挂载**: `-v $(pwd)/config:/iptv-api/config`
- **结果挂载**: `-v $(pwd)/output:/iptv-api/output`
- **源文件挂载**: `-v $(pwd)/source.json:/iptv-api/source.json`

### 独立部署 MoonTVPlus (仅前端)

如果需要连接远程的 IPTV-TVBox 后端：

```bash
docker run -d \
  --name moontv \
  --restart on-failure \
  -p 3000:3000 \
  -e USERNAME=admin \
  -e PASSWORD=admin \
  -e NEXT_PUBLIC_STORAGE_TYPE=redis \
  -e REDIS_URL=redis://<storage-host>:6379 \
  ghcr.io/mtvpls/moontvplus:latest
```

- **存储可选**: `REDIS_URL` 可指向 Redis 或 Kvrocks
- **数据持久化**: 建议确保存储端开启持久化

## 🛠️ 常用命令

```bash
# 更新镜像
docker-compose pull

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f iptv-tvbox
```

## 🔗 资源与致谢

- **前端播放器**: [MoonTVPlus](https://github.com/mtvpls/MoonTVPlus) (感谢 mtvpls 的杰出工作)
- **灵感来源**: [iptv-checker](https://github.com/zhimin-dev/iptv-checker)
- **EPG 数据**: [webgrabplus-siteinipack](https://github.com/SilentButeo2/webgrabplus-siteinipack)

## ⚠️ 免责声明

本项目仅供学习交流使用，所有数据源均来自互联网公开渠道，本项目不生产、不存储任何视频文件。请勿用于商业用途。
