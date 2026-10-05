#!/usr/bin/env python3
"""核对一份精读笔记：正文里加粗的数字，是否都在核心数字速查表里出现。

为什么必须用这个脚本，而不要自己核对：
人工比对两处数字列表是一件确定性的、重复的、且容易看漏的工作——
今天实测同一个模型做类似的核对任务，三次给出三个不同答案。
这一步的正确性不能靠推理保证。

用法:
    python3 scripts/check_numbers.py "<笔记.md>"
    python3 scripts/check_numbers.py "<笔记.md>" --table-heading "核心数字速查表"

退出码: 0 全部收齐 / 1 有遗漏 / 2 用法或文件错误
只用 Python 标准库，需要 3.8+。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_HEADING = "核心数字速查表"
NUM = re.compile(r"\d+(?:[.,]\d+)*")
BOLD = re.compile(r"\*\*([^*\n]+)\*\*")
# 正文里这些加粗项带数字但不属于「结论性数字」，不要求进速查表
SKIP = re.compile(
    r"^(?:\d+[.、)]\s)"            # 以编号开头的小标题，如 "1. 摘要…"
    r"|arXiv|§|Fig\.|Table|附录|第\s*\d+\s*[章节页]"
    r"|v\d+\s|20\d{2}-\d{2}"        # 版本号、日期
    r"|\[\d+\]"                     # 参考文献编号，如 "Voyager [54]"
    r"|\b[A-Z]\.\d+(?:\.\d+)*"      # 附录小节号，如 "A.4.3"、"B.4.5"
)


def split_body_and_table(text: str, heading: str) -> tuple[str, str]:
    """按速查表的标题行切开正文和表格。"""
    marker = re.search(rf"^#{{1,6}}\s*.*{re.escape(heading)}.*$", text, re.M)
    if not marker:
        sys.exit(f"✗ 找不到标题含「{heading}」的小节。用 --table-heading 指定实际标题。")
    return text[: marker.start()], text[marker.end() :]


def numbers_in(fragment: str) -> set[str]:
    return {n.replace(",", "") for n in NUM.findall(fragment)}


def main() -> int:
    ap = argparse.ArgumentParser(description="核对精读笔记的数字是否收齐进速查表。")
    ap.add_argument("note", help="笔记 markdown 文件路径")
    ap.add_argument("--table-heading", default=DEFAULT_HEADING,
                    help=f"速查表小节的标题关键词（默认：{DEFAULT_HEADING}）")
    ap.add_argument("--max-len", type=int, default=30,
                    help="超过这个长度的加粗项视为整句引文，跳过（默认 30）")
    args = ap.parse_args()

    path = Path(args.note)
    if not path.is_file():
        sys.exit(f"✗ 读不到文件：{path}")

    body, table = split_body_and_table(path.read_text(encoding="utf-8"),
                                       args.table_heading)
    table_nums = numbers_in(table)

    missing: list[tuple[str, list[str]]] = []
    for item in sorted(set(BOLD.findall(body))):
        item = item.strip()
        if len(item) > args.max_len or SKIP.search(item):
            continue
        nums = sorted(numbers_in(item))
        if nums and not any(n in table_nums for n in nums):
            missing.append((item, nums))

    if not missing:
        print(f"✓ 正文里的结论性数字都在「{args.table_heading}」中。")
        return 0

    print(f"✗ 以下 {len(missing)} 项在正文中加粗，但速查表里找不到对应数值：\n")
    for item, nums in missing:
        print(f"  · {item}        → {', '.join(nums)}")
    print("\n逐条判断：是结论性数字就补进速查表；是引文内部或章节号就无需处理。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
