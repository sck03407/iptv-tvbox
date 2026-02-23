from __future__ import annotations

import os
import socket
import time
from http.client import IncompleteRead
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit, quote
from urllib.request import Request, urlopen

# Set global timeout
socket.setdefaulttimeout(10)

def normalize_url(url: str) -> str:
    # Fix: Handle non-ASCII characters in URL (including path, query, fragment)
    parts = urlsplit(url)
    
    # Handle hostname with punycode if it contains non-ASCII
    netloc = parts.netloc
    try:
        netloc = netloc.encode('idna').decode('ascii')
    except Exception:
        pass

    # Encode path, query, fragment
    # 'safe' parameter specifies characters that should NOT be quoted
    # We keep existing % to avoid double encoding
    path = quote(parts.path, safe="/%:@&=+$,;")
    query = quote(parts.query, safe="=&%:@+$,;")
    fragment = quote(parts.fragment, safe="%:@&=+$,;")
    
    return urlunsplit((parts.scheme, netloc, path, query, fragment))

def try_request(url: str, method: str, max_retries: int = 2):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Connection": "close",
    }
    safe_url = normalize_url(url)
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            req = Request(safe_url, method=method, headers=headers)
            # Slightly longer timeout for retries
            timeout = 10 + (attempt * 5)
            with urlopen(req, timeout=timeout) as resp:
                status = resp.getcode() or 0
                data = b""
                if method != "HEAD":
                    try:
                        data = resp.read(2048)
                    except IncompleteRead as e:
                        data = e.partial
                return status, data
        except HTTPError as e:
            # 5xx errors might be transient
            if 500 <= e.code < 600 and attempt < max_retries:
                last_exception = e
                time.sleep(1)
                continue
            raise e
        except (URLError, TimeoutError, ConnectionError, IncompleteRead, socket.timeout) as e:
            last_exception = e
            if attempt < max_retries:
                time.sleep(1)
                continue
    
    if last_exception:
        raise last_exception
    raise URLError("Unknown error")

def classify_status(status: int) -> str:
    if 200 <= status < 400:
        return "valid"
    if status in (404, 410):
        return "invalid"
    return "unknown"

def probe_once(url: str) -> str:
    try:
        status, _ = try_request(url, "HEAD")
        head_result = classify_status(status)
        if head_result != "unknown":
            return head_result
    except HTTPError as e:
        if e.code in (404, 410):
            return "invalid"
    except (URLError, TimeoutError, socket.timeout, IncompleteRead, ConnectionError):
        return "unknown"

    try:
        status, data = try_request(url, "GET")
        get_result = classify_status(status)
        if get_result == "valid":
            return "valid" if data.strip() else "invalid"
        return get_result
    except HTTPError as e:
        return "invalid" if e.code in (404, 410) else "unknown"
    except (URLError, TimeoutError, socket.timeout, IncompleteRead, ConnectionError):
        return "unknown"

def classify_url(url: str, attempts: int = 2) -> str:
    invalid_hits = 0
    for _ in range(attempts):
        result = probe_once(url)
        if result == "valid":
            return "valid"
        if result == "invalid":
            invalid_hits += 1
    return "invalid" if invalid_hits >= attempts else "unknown"

def main():
    path = Path("config/subscribe.txt")
    try:
        original = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        original = path.read_text(encoding="gbk", errors="ignore")
        
    lines = original.splitlines()
    
    kept = []
    removed = []
    unknown = []
    total_checked = 0
    valid_count = 0
    invalid_count = 0
    unknown_count = 0
    
    for line in lines:
        s = line.strip()
        if not s or s.startswith("#") or (s.startswith("[") and s.endswith("]")):
            kept.append(line)
            continue
        if s.startswith("http://") or s.startswith("https://"):
            total_checked += 1
            status = classify_url(s)
            if status == "valid":
                valid_count += 1
                kept.append(line)
            elif status == "invalid":
                invalid_count += 1
                removed.append(s)
            else:
                unknown_count += 1
                unknown.append(s)
                kept.append(line)
            continue
        kept.append(line)
    
    new_content = "\n".join(kept)
    if original.endswith("\n"):
        new_content += "\n"
    
    if new_content != original:
        path.write_text(new_content, encoding="utf-8")
    
    print(f"checked_total={total_checked}")
    print(f"valid_total={valid_count}")
    print(f"invalid_total={invalid_count}")
    print(f"unknown_total={unknown_count}")
    print(f"removed_total={len(removed)}")
    if removed:
        print("removed_urls=")
        for url in removed:
            print(url)

    summary_lines = [
        "## 订阅源体检报告",
        f"- 检测总数: {total_checked}",
        f"- 有效: {valid_count}",
        f"- 无效(已剔除): {invalid_count}",
        f"- 不确定(保留): {unknown_count}",
    ]
    if removed:
        summary_lines.append("")
        summary_lines.append("### 已剔除链接")
        for url in removed[:50]:
            summary_lines.append(f"- {url}")
        if len(removed) > 50:
            summary_lines.append(f"- ... 其余 {len(removed) - 50} 条已省略")
    if unknown:
        summary_lines.append("")
        summary_lines.append("### 不确定(保留)链接")
        for url in unknown[:50]:
            summary_lines.append(f"- {url}")
        if len(unknown) > 50:
            summary_lines.append(f"- ... 其余 {len(unknown) - 50} 条已省略")
    
    report_content = "\n".join(summary_lines) + "\n"
    
    # Write to GitHub Summary
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(report_content)

if __name__ == "__main__":
    main()
