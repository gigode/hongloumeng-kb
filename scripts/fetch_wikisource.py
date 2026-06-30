from __future__ import annotations

import argparse
import re
import time
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.kb import RAW_DIR, chapter_file_stem, ensure_dirs, write_json

API_URL = "https://zh.wikisource.org/w/api.php"
USER_AGENT = "hongloumeng-kb/0.1 (https://github.com/gigode/hongloumeng-kb; research prototype)"

CHAPTER_TITLES = {
    "001": "甄士隐梦幻识通灵 贾雨村风尘怀闺秀",
    "002": "贾夫人仙逝扬州城 冷子兴演说荣国府",
    "003": "贾雨村夤缘复旧职 林黛玉抛父进京都",
    "004": "薄命女偏逢薄命郎 葫芦僧乱判葫芦案",
    "005": "游幻境指迷十二钗 饮仙醪曲演红楼梦",
}


def _clean_text(value: str) -> str:
    value = value.replace("\xa0", " ")
    value = re.sub(r"\[[^\]]+\]", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def _extract_paragraphs(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    root = soup.select_one(".mw-parser-output") or soup

    for selector in [
        "style",
        "script",
        ".mw-editsection",
        "sup.reference",
        ".reference",
        ".printfooter",
        ".catlinks",
        ".navbox",
        ".metadata",
        "table",
    ]:
        for node in root.select(selector):
            node.decompose()

    paragraphs: list[str] = []
    for node in root.find_all(["p", "div", "li"], recursive=True):
        classes = set(node.get("class") or [])
        if node.name == "div" and not (classes & {"poem", "ws-poem"}):
            continue
        text = _clean_text(node.get_text(" ", strip=True))
        if not text:
            continue
        if "上一回" in text or "下一回" in text or "返回目录" in text:
            continue
        if len(text) < 4:
            continue
        if text not in paragraphs:
            paragraphs.append(text)
    return paragraphs


def fetch_chapter(chapter_id: str, insecure: bool = False) -> dict:
    page = f"紅樓夢/第{chapter_id}回"
    response = requests.get(
        API_URL,
        params={
            "action": "parse",
            "page": page,
            "prop": "text|displaytitle",
            "format": "json",
            "formatversion": "2",
            "variant": "zh-hans",
        },
        headers={"User-Agent": USER_AGENT},
        timeout=45,
        verify=not insecure,
    )
    response.raise_for_status()
    payload = response.json()["parse"]
    paragraphs = _extract_paragraphs(payload["text"])
    title = CHAPTER_TITLES.get(chapter_id, payload.get("displaytitle", f"第{chapter_id}回"))
    return {
        "id": chapter_id,
        "title": title,
        "source_page": page,
        "source_url": f"https://zh.wikisource.org/wiki/{page}",
        "paragraphs": paragraphs,
    }


def write_raw_chapter(chapter: dict) -> Path:
    stem = chapter_file_stem(chapter["id"], chapter["title"])
    path = RAW_DIR / f"{stem}.md"
    lines = [
        f"# [{chapter['id']}] {chapter['title']}",
        "",
        f"> Source: {chapter['source_url']}",
        "",
    ]
    for idx, paragraph in enumerate(chapter["paragraphs"], 1):
        lines.append(f"[{idx}] {paragraph}")
        lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapters", type=int, default=5)
    parser.add_argument("--insecure", action="store_true", help="Disable TLS verification for broken local CA stores.")
    args = parser.parse_args()

    ensure_dirs()
    chapters = []
    for number in range(1, args.chapters + 1):
        chapter_id = f"{number:03d}"
        chapter = fetch_chapter(chapter_id, insecure=args.insecure)
        if len(chapter["paragraphs"]) < 5:
            raise RuntimeError(f"Chapter {chapter_id} returned too few paragraphs: {len(chapter['paragraphs'])}")
        raw_path = write_raw_chapter(chapter)
        chapters.append({key: chapter[key] for key in ["id", "title", "source_page", "source_url"]} | {
            "raw_path": str(raw_path.relative_to(RAW_DIR.parents[1])),
            "paragraph_count": len(chapter["paragraphs"]),
        })
        time.sleep(0.2)

    write_json(RAW_DIR.parents[1] / "data" / "chapters.json", chapters)


if __name__ == "__main__":
    main()
