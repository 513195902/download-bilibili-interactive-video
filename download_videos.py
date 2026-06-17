import csv
import os
import re
import time
import requests
from datetime import datetime
from urllib.parse import urlparse


# ==============================
# 配置
# ==============================

CSV_FILE = "interactive_tree.csv"
DOWNLOAD_DIR = "downloads"

# 如果 mp4_url 过期，可以填 AID，让脚本根据 cid 自动刷新 playurl
# 例如 BV1hE411B78P 对应 AID=74625133
# 不想自动刷新就保持 None
AID = 74625133

# 一般不需要 Cookie
# 如果遇到 403 / 412，再粘浏览器 Cookie
COOKIE = r"""
""".strip()

RETRY = 3
CHUNK_SIZE = 1024 * 1024
SLEEP_BETWEEN_DOWNLOADS = 0.3


# ==============================
# 工具函数
# ==============================

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def build_headers():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/144.0.0.0 Safari/537.36"
        ),
        "Referer": "https://www.bilibili.com/",
    }

    if COOKIE:
        headers["Cookie"] = COOKIE

    return headers


def safe_filename(text, max_len=80):
    if text is None:
        text = ""

    text = str(text).strip()

    text = re.sub(r'[\\/:*?"<>|]', "_", text)
    text = re.sub(r"\s+", " ", text)

    if len(text) > max_len:
        text = text[:max_len]

    return text


def get_ext_from_url(url):
    path = urlparse(url).path

    _, ext = os.path.splitext(path)

    if ext:
        return ext

    return ".mp4"


# ==============================
# 通过 cid 刷新 playurl
# ==============================

def refresh_playurl(aid, cid):
    if not aid or not cid:
        return ""

    api = "https://api.bilibili.com/x/player/playurl"

    params = {
        "avid": aid,
        "cid": cid,
    }

    try:
        r = requests.get(
            api,
            params=params,
            headers=build_headers(),
            timeout=30,
        )

        data = r.json()

        if data.get("code") != 0:
            log(f"刷新 playurl 失败 cid={cid}, code={data.get('code')}")
            return ""

        durl = data.get("data", {}).get("durl")

        if not durl:
            log(f"刷新 playurl 没有 durl cid={cid}")
            return ""

        return durl[0].get("url", "")

    except Exception as e:
        log(f"刷新 playurl 异常 cid={cid}: {e}")
        return ""


# ==============================
# 下载单个文件
# ==============================

def download_file(url, filepath):
    temp_path = filepath + ".part"

    headers = build_headers()

    downloaded = 0

    if os.path.exists(temp_path):
        downloaded = os.path.getsize(temp_path)
        if downloaded > 0:
            headers["Range"] = f"bytes={downloaded}-"

    with requests.get(
        url,
        headers=headers,
        stream=True,
        timeout=60,
    ) as r:

        if r.status_code in (403, 404, 412):
            return False, f"HTTP {r.status_code}"

        if r.status_code not in (200, 206):
            return False, f"HTTP {r.status_code}"

        mode = "ab" if r.status_code == 206 and downloaded > 0 else "wb"

        total = r.headers.get("Content-Length")

        with open(temp_path, mode) as f:
            for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)

    os.replace(temp_path, filepath)

    return True, "OK"


# ==============================
# 读取 CSV
# ==============================

def read_rows(csv_file):
    with open(csv_file, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


# ==============================
# 主程序
# ==============================

def main():
    if not os.path.exists(CSV_FILE):
        raise FileNotFoundError(f"找不到 {CSV_FILE}")

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    rows = read_rows(CSV_FILE)

    log(f"读取到 {len(rows)} 条记录")

    success_count = 0
    fail_count = 0
    skip_count = 0

    for index, row in enumerate(rows, start=1):
        edge_id = row.get("edge_id", "").strip()
        cid = row.get("cid", "").strip()
        title = row.get("title", "").strip()
        choice_text = row.get("choice_text", "").strip()
        mp4_url = row.get("mp4_url", "").strip()

        if not cid:
            log(f"[{index}/{len(rows)}] 跳过，无 cid edge={edge_id}")
            skip_count += 1
            continue

        name_part = safe_filename(choice_text or title or "video")

        filename = f"{edge_id}_{cid}_{name_part}.mp4"
        filepath = os.path.join(DOWNLOAD_DIR, filename)

        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            log(f"[{index}/{len(rows)}] 已存在，跳过: {filename}")
            skip_count += 1
            continue

        if not mp4_url and AID:
            log(f"[{index}/{len(rows)}] 无 mp4_url，尝试刷新 cid={cid}")
            mp4_url = refresh_playurl(AID, cid)

        if not mp4_url:
            log(f"[{index}/{len(rows)}] 失败，无可用 URL edge={edge_id}, cid={cid}")
            fail_count += 1
            continue

        log(f"[{index}/{len(rows)}] 下载 edge={edge_id}, cid={cid}")
        log(f"文件: {filename}")

        ok = False
        last_msg = ""

        for attempt in range(1, RETRY + 1):
            ok, msg = download_file(mp4_url, filepath)
            last_msg = msg

            if ok:
                break

            log(f"下载失败 attempt={attempt}, msg={msg}")

            # 如果 URL 过期或被拒绝，尝试用 cid 刷新
            if AID and msg in ("HTTP 403", "HTTP 404", "HTTP 412"):
                log(f"尝试刷新 playurl cid={cid}")
                new_url = refresh_playurl(AID, cid)

                if new_url:
                    mp4_url = new_url

            time.sleep(1)

        if ok:
            size_mb = os.path.getsize(filepath) / 1024 / 1024
            log(f"完成: {filename} ({size_mb:.2f} MB)")
            success_count += 1
        else:
            log(f"最终失败: edge={edge_id}, cid={cid}, reason={last_msg}")
            fail_count += 1

        time.sleep(SLEEP_BETWEEN_DOWNLOADS)

    print("\n" + "=" * 60)
    log("下载任务结束")
    log(f"成功: {success_count}")
    log(f"跳过: {skip_count}")
    log(f"失败: {fail_count}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"程序异常: {e}")