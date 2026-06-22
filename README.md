<div align="center">

# Bilibili Interactive Video Exporter

Export, analyze, and download all branches of Bilibili interactive videos.

[简体中文](README_zh.md) | English

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
> Bilibili APIs may change at any time. This project may require updates accordingly.

## Introduction

**Bilibili Interactive Video Exporter** is a Python tool for parsing Bilibili interactive videos.

Given a BV ID, it automatically retrieves the video `aid`, initial `cid`, and interactive graph version `graph_version`. It then recursively traverses the entire interactive story tree and exports every branch node with its `edge_id`, `cid`, title, option text, and temporary MP4 URL.

The project also includes a separate downloader script that reads the exported `interactive_tree.csv` and batch downloads the video segment for each interactive node.

## Features

- Parse Bilibili interactive videos from a BV ID
- Automatically retrieve `aid`, initial `cid`, and `graph_version`
- Recursively traverse the interactive story tree
- Export all branch nodes to `interactive_tree.csv`
- Extract `edge_id`, `cid`, title, option text, and MP4 URL
- Batch download all interactive video segments
- Refresh expired temporary MP4 URLs using `cid`
- Works without login cookies for many public videos

## Project Structure

```text
.
├── main.py
├── download_videos.py
├── pyproject.toml
├── uv.lock
├── README.md
└── README_zh.md
````

## Requirements

* Python 3.12+
* requests

Using uv:

```bash
uv sync
```

Using pip:

```bash
pip install requests
```

## Usage

### 1. Export the interactive video tree

```bash
python main.py
```

Enter a BV ID:

```text
请输入BV号: BV1xxxxxxxxx
```

The script will generate:

```text
interactive_tree.csv
```

The CSV contains:

| Field         | Description                               |
| ------------- | ----------------------------------------- |
| `parent_edge` | Parent node edge ID                       |
| `edge_id`     | Current node edge ID                      |
| `title`       | Current node title                        |
| `choice_text` | Option text used to enter this node       |
| `cid`         | Video CID of the current node             |
| `is_leaf`     | Whether this node is a leaf / ending node |
| `mp4_url`     | Temporary MP4 URL resolved from the CID   |

### 2. Download video segments

Make sure `interactive_tree.csv` and `download_videos.py` are in the same directory.

```bash
python download_videos.py
```

Downloaded files will be saved to:

```text
downloads/
```

Filename format:

```text
edge_id_cid_choice_text.mp4
```

## Cookie

Most public videos do not require cookies.

If you encounter `403`, `412`, or failed `playurl` requests, you may configure your browser Cookie in the script:

```python
COOKIE = r"""
Paste your Cookie here
""".strip()
```

Never commit your Cookie to GitHub.

## Notes

MP4 URLs returned by Bilibili are temporary signed URLs and may expire. It is recommended to keep stable metadata such as `edge_id`, `cid`, `title`, and `choice_text`, and refresh playback URLs when needed.

## Anti-Abuse Recommendations

* Do not run high-concurrency downloads
* Do not send high-frequency API requests
* Keep a delay between downloads
* Avoid repeatedly refreshing `playurl`
* Avoid using login cookies when anonymous access works

## Disclaimer

This project is intended for learning, research, and personal backup purposes only.

This project does not bypass payment, permission, login, or platform access restrictions. Please make sure you have the legal right to download and process the video content.

Do not use this project for commercial redistribution, mass re-uploading, abusive requests, or any activity that violates platform rules.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=513195902/download-bilibili-interactive-video\&type=Date)](https://www.star-history.com/#513195902/download-bilibili-interactive-video&Date)

```
