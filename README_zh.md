````md
<div align="center">

# Bilibili Interactive Video Exporter

导出、分析并下载 B 站互动视频的全部分支节点。

简体中文 | [English](README.md)

<p>
  <img src="https://img.shields.io/badge/python-3.12%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/status-stable-brightgreen" alt="Status">
  <img src="https://img.shields.io/badge/platform-Bilibili-00A1D6" alt="Platform">
  <img src="https://img.shields.io/badge/dependency-requests-orange" alt="Dependency">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
</p>

</div>

---

> [!WARNING]
> B 站接口可能随时变动，请及时更新到最新版本。

## 简介

**Bilibili Interactive Video Exporter** 是一个用于解析 B 站互动视频的 Python 工具。

它可以根据一个 BV 号自动获取视频的 `aid`、首页 `cid` 和互动剧情图版本 `graph_version`，递归遍历互动视频的全部剧情节点，并导出每个分支节点对应的 `edge_id`、`cid`、标题、选项文本和临时 MP4 地址。

项目还提供了独立的视频下载脚本，可以读取导出的 `interactive_tree.csv`，批量下载每个互动节点对应的视频片段。

## 功能特点

- 通过 BV 号解析 B 站互动视频
- 自动获取 `aid`、首页 `cid` 和 `graph_version`
- 递归遍历互动视频剧情树
- 导出所有分支节点到 `interactive_tree.csv`
- 提取 `edge_id`、`cid`、标题、选项文本和 MP4 地址
- 批量下载全部互动视频片段
- 支持通过 `cid` 刷新过期的临时 MP4 地址
- 多数公开视频无需登录 Cookie

## 项目结构

```text
.
├── main.py
├── download_videos.py
├── pyproject.toml
├── uv.lock
├── README.md
└── README_zh.md
````

## 环境要求

* Python 3.12+
* requests

使用 uv：

```bash
uv sync
```

使用 pip：

```bash
pip install requests
```

## 使用方法

### 1. 导出互动视频剧情树

```bash
python main.py
```

输入 BV 号：

```text
请输入BV号: BV1xxxxxxxxx
```

脚本会生成：

```text
interactive_tree.csv
```

CSV 包含以下字段：

| 字段            | 说明                   |
| ------------- | -------------------- |
| `parent_edge` | 父节点 edge ID          |
| `edge_id`     | 当前节点 edge ID         |
| `title`       | 当前节点标题               |
| `choice_text` | 从父节点进入当前节点时选择的选项文本   |
| `cid`         | 当前节点对应的视频 CID        |
| `is_leaf`     | 是否为叶子节点 / 结局节点       |
| `mp4_url`     | 根据 CID 获取到的临时 MP4 地址 |

### 2. 下载视频片段

确保 `interactive_tree.csv` 和 `download_videos.py` 位于同一目录。

```bash
python download_videos.py
```

下载文件会保存到：

```text
downloads/
```

文件名格式：

```text
edge_id_cid_choice_text.mp4
```

## Cookie

大多数公开视频无需 Cookie。

如果遇到 `403`、`412` 或 `playurl` 请求失败，可以在脚本中配置浏览器 Cookie：

```python
COOKIE = r"""
这里粘贴你的 Cookie
""".strip()
```

请勿将 Cookie 提交到 GitHub。

## 说明

B 站返回的 MP4 地址通常是带签名和过期时间的临时地址。建议长期保存 `edge_id`、`cid`、`title` 和 `choice_text` 等稳定信息，需要下载时再重新获取播放地址。

## 防风控建议

* 不要并发下载大量视频
* 不要高频请求接口
* 下载之间保留适当间隔
* 不要频繁刷新 `playurl`
* 匿名访问可用时尽量不要使用登录 Cookie

## 免责声明

本项目仅供学习、研究和个人备份使用。

本项目不会绕过付费、权限、登录或平台访问限制。请确保你对下载和处理的视频内容拥有合法使用权。

请勿将本项目用于商业转载、批量搬运、恶意请求或其他违反平台规则的用途。

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=YOUR_NAME/YOUR_REPO\&type=Date)](https://www.star-history.com/#YOUR_NAME/YOUR_REPO&Date)

```
```
