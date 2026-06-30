from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.kb import RAW_DIR, TAGGED_DIR, chapter_file_stem, ensure_dirs, read_json

LEXICON = {
    "@": [
        ("甄士隐", "甄士隐"),
        ("贾雨村", "贾雨村"),
        ("娇杏", "娇杏"),
        ("英莲", "甄英莲"),
        ("甄英莲", "甄英莲"),
        ("封肃", "封肃"),
        ("冷子兴", "冷子兴"),
        ("林如海", "林如海"),
        ("贾敏", "贾敏"),
        ("黛玉", "林黛玉"),
        ("林黛玉", "林黛玉"),
        ("贾母", "贾母"),
        ("王夫人", "王夫人"),
        ("邢夫人", "邢夫人"),
        ("贾政", "贾政"),
        ("贾赦", "贾赦"),
        ("贾珍", "贾珍"),
        ("贾琏", "贾琏"),
        ("王熙凤", "王熙凤"),
        ("凤姐", "王熙凤"),
        ("宝玉", "贾宝玉"),
        ("贾宝玉", "贾宝玉"),
        ("迎春", "贾迎春"),
        ("探春", "贾探春"),
        ("惜春", "贾惜春"),
        ("薛蟠", "薛蟠"),
        ("薛姨妈", "薛姨妈"),
        ("宝钗", "薛宝钗"),
        ("薛宝钗", "薛宝钗"),
        ("香菱", "香菱"),
        ("秦可卿", "秦可卿"),
        ("可卿", "秦可卿"),
        ("秦氏", "秦可卿"),
        ("警幻仙姑", "警幻仙姑"),
        ("秦钟", "秦钟"),
        ("刘姥姥", "刘姥姥"),
        ("和尚", "癞头和尚"),
        ("道人", "跛足道人"),
    ],
    "=": [
        ("荣国府", "荣国府"),
        ("宁国府", "宁国府"),
        ("贾府", "贾府"),
        ("扬州", "扬州"),
        ("京都", "京都"),
        ("金陵", "金陵"),
        ("姑苏", "姑苏"),
        ("葫芦庙", "葫芦庙"),
        ("太虚幻境", "太虚幻境"),
        ("会芳园", "会芳园"),
        ("梨香院", "梨香院"),
    ],
    "&": [
        ("贾家", "贾家"),
        ("林家", "林家"),
        ("薛家", "薛家"),
        ("王家", "王家"),
        ("史家", "史家"),
        ("甄家", "甄家"),
        ("荣国府", "荣国府"),
        ("宁国府", "宁国府"),
    ],
    "#": [
        ("丫鬟", "丫鬟"),
        ("姑娘", "姑娘"),
        ("奶娘", "奶娘"),
        ("王妃", "王妃"),
        ("进士", "进士"),
        ("知府", "知府"),
        ("门子", "门子"),
        ("公子", "公子"),
        ("小姐", "小姐"),
        ("仙姑", "仙姑"),
    ],
    "•": [
        ("通灵宝玉", "通灵宝玉"),
        ("宝玉", "通灵宝玉"),
        ("金锁", "金锁"),
        ("风月宝鉴", "风月宝鉴"),
    ],
    "{": [
        ("好了歌", "好了歌"),
        ("金陵十二钗", "金陵十二钗"),
        ("红楼梦曲", "红楼梦曲"),
    ],
    "_": [
        ("梦", "梦"),
        ("梦幻", "梦幻"),
        ("情", "情"),
        ("空", "空"),
        ("色", "色"),
        ("风月", "风月"),
        ("薄命", "薄命"),
        ("因缘", "因缘"),
    ],
    "%": [
        ("一日", "一日"),
        ("次日", "次日"),
        ("这日", "这日"),
        ("那日", "那日"),
        ("今日", "今日"),
        ("五更", "五更"),
    ],
}


def _token(tag: str, surface: str, canonical: str) -> str:
    if surface == canonical:
        return f"〖{tag}{surface}〗"
    return f"〖{tag}{surface}|{canonical}〗"


def annotate_text(text: str) -> str:
    replacements = []
    for tag, items in LEXICON.items():
        for surface, canonical in items:
            replacements.append((surface, tag, canonical))
    replacements.sort(key=lambda item: len(item[0]), reverse=True)

    protected = re.compile(r"〖[^〗]+〗")
    for surface, tag, canonical in replacements:
        pattern = re.compile(re.escape(surface))
        cursor = 0
        parts = []
        for match in pattern.finditer(text):
            if any(a <= match.start() < b for a, b in [(m.start(), m.end()) for m in protected.finditer(text)]):
                continue
            parts.append(text[cursor:match.start()])
            parts.append(_token(tag, surface, canonical))
            cursor = match.end()
        if parts:
            parts.append(text[cursor:])
            text = "".join(parts)
    return text


def main() -> None:
    ensure_dirs()
    TAGGED_DIR.mkdir(parents=True, exist_ok=True)
    chapters = read_json(RAW_DIR.parents[1] / "data" / "chapters.json", [])
    for chapter in chapters[:5]:
        raw_path = RAW_DIR.parents[1] / chapter["raw_path"]
        content = raw_path.read_text(encoding="utf-8")
        tagged_lines = []
        for line in content.splitlines():
            tagged_lines.append(annotate_text(line) if line.startswith("[") else line)
        tagged = "\n".join(tagged_lines) + "\n"
        out = TAGGED_DIR / f"{chapter_file_stem(chapter['id'], chapter['title'])}.tagged.md"
        out.write_text(tagged, encoding="utf-8")


if __name__ == "__main__":
    main()
