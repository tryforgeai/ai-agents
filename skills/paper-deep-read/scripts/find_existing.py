#!/usr/bin/env python3
"""动笔前查 vault：这篇是不是已经有笔记了？用户读过哪些论文（谱系对比用）？

为什么用脚本：「vault 里现在有什么」是一个查找问题，靠记忆或印象会漏。

用法:
    python3 scripts/find_existing.py --vault "<vault 目录>" "<论文名或关键词>" ["<arXiv 编号>" ...]

输出:
    1. 疑似同一篇的已有笔记（文件名命中论文名，或开头 15 行命中 arXiv 编号）
    2. vault 里所有已有的精读笔记（谱系表从这里挑「已读过的论文」）
    3. 课程阅读清单的位置（如果存在）

退出码: 0 没有同一篇的笔记 / 1 找到疑似同一篇（先问用户：更新还是重写）/ 2 用法错误
只用 Python 标准库，需要 3.8+。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PATTERN = "*论文精读笔记.md"
ARXIV = re.compile(r"\d{4}\.\d{4,5}(v\d+)?")
READING_LISTS = ["course/reading-list.zh.md", "reading-list.zh.md"]


def main() -> int:
    ap = argparse.ArgumentParser(description="查 vault 里已有的精读笔记。")
    ap.add_argument("--vault", required=True, help="存放精读笔记的 vault 目录")
    ap.add_argument("terms", nargs="+", help="论文名、简称或 arXiv 编号")
    args = ap.parse_args()

    vault = Path(args.vault).expanduser()
    if not vault.is_dir():
        print(f"✗ 不是目录：{vault}")
        return 2

    notes = sorted(vault.rglob(PATTERN))
    terms = [t.lower() for t in args.terms if t.strip()]
    hits = []
    for note in notes:
        try:
            head = "\n".join(note.read_text(encoding="utf-8").splitlines()[:15])
        except OSError:
            continue
        # 论文名只比对文件名（正文里常提到别的论文，会误报）；
        # arXiv 编号再比对开头 15 行的来源信息
        name = note.name.lower()
        matched = [t for t in terms if t in name
                   or (ARXIV.fullmatch(t) and t in head.lower())]
        if matched:
            hits.append((note, matched))

    if hits:
        print("⚠️ 疑似已有同一篇的笔记：")
        for note, matched in hits:
            print(f"  · {note.relative_to(vault)}    （命中：{', '.join(matched)}）")
    else:
        print("✓ 没找到同一篇的笔记，可以新建。")

    print(f"\nvault 里已有的精读笔记（{len(notes)} 篇，谱系对比从这里选）：")
    for note in notes:
        print(f"  · {note.name.replace(' 论文精读笔记.md', '')}")

    for rel in READING_LISTS:
        if (vault / rel).is_file():
            print(f"\n课程阅读清单：{rel}")
            break

    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
