import requests
import csv
import re
import time
from datetime import datetime


# ==============================
# 配置
# ==============================

# 一般不需要 Cookie。
# 如果遇到 412 或 playurl 失败，再把浏览器 F12 里的 Cookie 粘进来。
COOKIE = r"""
""".strip()

REQUEST_INTERVAL = 0.25

session = requests.Session()

visited = set()
rows = []
edge_to_cid = {}


# ==============================
# 工具函数
# ==============================

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def build_headers(bvid=None):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/144.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.bilibili.com/",
    }

    if bvid:
        headers["Referer"] = f"https://www.bilibili.com/video/{bvid}/"

    if COOKIE:
        headers["Cookie"] = COOKIE
        headers["Origin"] = "https://www.bilibili.com"

    return headers


def extract_buvid_from_cookie():
    if not COOKIE:
        return ""

    m = re.search(r"buvid3=([^;]+)", COOKIE)

    if m:
        return m.group(1)

    return ""


# ==============================
# 获取视频信息
# ==============================

def get_video_info(bvid):
    log(f"获取视频信息: {bvid}")

    url = "https://api.bilibili.com/x/web-interface/view"

    r = session.get(
        url,
        params={"bvid": bvid},
        headers=build_headers(bvid),
        timeout=30
    )

    data = r.json()

    if data.get("code") != 0:
        raise Exception(f"view接口失败: {data}")

    info = data["data"]

    aid = info["aid"]
    cid = info["cid"]
    is_stein_gate = info.get("rights", {}).get("is_stein_gate")

    log(f"aid={aid}")
    log(f"首页cid={cid}")
    log(f"is_stein_gate={is_stein_gate}")

    if is_stein_gate != 1:
        raise Exception("这个视频不是互动视频")

    return info


# ==============================
# 获取 graph_version
# ==============================

def get_graph_version(aid, cid, bvid):
    log("获取 graph_version")

    url = "https://api.bilibili.com/x/player/v2"

    r = session.get(
        url,
        params={
            "aid": aid,
            "cid": cid,
        },
        headers=build_headers(bvid),
        timeout=30
    )

    data = r.json()

    if data.get("code") != 0:
        raise Exception(f"player/v2失败: {data}")

    graph_version = (
        data.get("data", {})
        .get("interaction", {})
        .get("graph_version")
    )

    if not graph_version:
        raise Exception("未找到 graph_version")

    log(f"graph_version={graph_version}")

    return graph_version


# ==============================
# 获取互动节点
# ==============================

def get_edge(aid, graph_version, edge_id, bvid):
    url = "https://api.bilibili.com/x/stein/edgeinfo_v2"

    params = {
        "platform": "pc",
        "graph_version": graph_version,
        "portal": 0,
        "screen": 0,
        "edge_id": edge_id,
        "choices": "",
        "aid": aid,
    }

    buvid = extract_buvid_from_cookie()

    if buvid:
        params["buvid"] = buvid

    r = session.get(
        url,
        params=params,
        headers=build_headers(bvid),
        timeout=30
    )

    if r.status_code != 200:
        print(r.text[:1000])
        raise Exception(f"edgeinfo HTTP失败: {r.status_code}")

    try:
        data = r.json()
    except Exception:
        print(r.text[:1000])
        raise Exception("edgeinfo 返回不是 JSON")

    if data.get("code") != 0:
        raise Exception(f"edgeinfo失败: {data}")

    return data


# ==============================
# 获取真实 mp4 地址
# ==============================

def get_playurl(aid, cid, bvid):
    if not cid:
        return ""

    url = "https://api.bilibili.com/x/player/playurl"

    r = session.get(
        url,
        params={
            "avid": aid,
            "cid": cid,
        },
        headers=build_headers(bvid),
        timeout=30
    )

    try:
        data = r.json()
    except Exception:
        return ""

    if data.get("code") != 0:
        log(f"playurl失败 cid={cid}, code={data.get('code')}")
        return ""

    durl = data.get("data", {}).get("durl")

    if not durl:
        log(f"playurl无durl cid={cid}")
        return ""

    url = durl[0].get("url", "")

    if url and str(cid) not in url:
        log(f"警告：返回URL里未出现cid={cid}")

    return url


# ==============================
# 记录 choices 中的 edge -> cid
# ==============================

def register_choice_cids(data):
    questions = (
        data.get("data", {})
        .get("edges", {})
        .get("questions", [])
    )

    count = 0

    for question in questions:
        for choice in question.get("choices", []):
            next_edge = choice.get("id")
            next_cid = choice.get("cid")

            if next_edge and next_cid:
                edge_to_cid[next_edge] = next_cid
                count += 1

    return count


# ==============================
# DFS 遍历互动树
# ==============================

def walk(
    aid,
    graph_version,
    edge_id,
    bvid,
    parent_edge=None,
    choice_text="ROOT",
):
    if edge_id in visited:
        return

    visited.add(edge_id)

    cid = edge_to_cid.get(edge_id)

    log(
        f"访问 edge={edge_id}, "
        f"cid={cid}, "
        f"choice={choice_text}"
    )

    data = get_edge(
        aid=aid,
        graph_version=graph_version,
        edge_id=edge_id,
        bvid=bvid,
    )

    node_data = data.get("data", {})

    title = node_data.get("title")
    is_leaf = node_data.get("is_leaf")

    mp4_url = get_playurl(
        aid=aid,
        cid=cid,
        bvid=bvid,
    )

    if mp4_url:
        log(f"mp4成功 edge={edge_id}")
    else:
        log(f"mp4为空 edge={edge_id}")

    rows.append({
        "parent_edge": parent_edge,
        "edge_id": edge_id,
        "title": title,
        "choice_text": choice_text,
        "cid": cid,
        "is_leaf": is_leaf,
        "mp4_url": mp4_url,
    })

    added = register_choice_cids(data)

    questions = (
        node_data
        .get("edges", {})
        .get("questions", [])
    )

    log(
        f"edge={edge_id} is_leaf={is_leaf}, "
        f"questions={len(questions)}, "
        f"new_cids={added}"
    )

    for question in questions:
        for choice in question.get("choices", []):
            next_edge = choice.get("id")
            option_text = choice.get("option", "")

            walk(
                aid=aid,
                graph_version=graph_version,
                edge_id=next_edge,
                bvid=bvid,
                parent_edge=edge_id,
                choice_text=option_text,
            )

            time.sleep(REQUEST_INTERVAL)


# ==============================
# 导出结果
# ==============================

def export_csv(filename="interactive_tree.csv"):
    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "parent_edge",
                "edge_id",
                "title",
                "choice_text",
                "cid",
                "is_leaf",
                "mp4_url",
            ]
        )

        writer.writeheader()
        writer.writerows(rows)

    log(f"已导出 {filename}")


# ==============================
# 主程序
# ==============================

def main():
    bvid = input("请输入BV号: ").strip()

    info = get_video_info(bvid)

    aid = info["aid"]
    first_cid = info["cid"]

    edge_to_cid[1] = first_cid

    graph_version = get_graph_version(
        aid=aid,
        cid=first_cid,
        bvid=bvid,
    )

    log("开始遍历互动树")

    walk(
        aid=aid,
        graph_version=graph_version,
        edge_id=1,
        bvid=bvid,
    )

    export_csv()

    log(f"完成，共导出 {len(rows)} 个节点")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"程序异常: {e}")