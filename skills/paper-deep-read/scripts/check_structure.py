#!/usr/bin/env python3
"""核对一份精读笔记的结构：必备章节、顺序、引文、批评条数、谱系表格、自测题。

为什么用脚本：这些都是有唯一答案的计数和查找，人工对 Done when 容易看漏。
脚本只负责**标出**问题；内容好不好（批评够不够硬、密度够不够）仍由你判断。

用法:
    python3 scripts/check_structure.py "<笔记.md>"

退出码: 0 结构齐全（可能带 ⚠️ 提醒）/ 1 有缺项 / 2 用法或文件错误
只用 Python 标准库，需要 3.8+。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# (名字, 匹配二级标题的正则)，顺序即要求的顺序
REQUIRED = [
    ("一句话总括", r"一句话总括"),
    ("动机与定位", r"动机"),
    ("方法精读", r"方法"),
    ("实验", r"实验"),
        ("谱系", r"谱系|对比地图"),
    ("批判性分析", r"批判"),
    ("复习自测题", r"自测"),
    ("核心数字速查表", r"速查表"),
]
H2 = re.compile(r"^##\s+(.+)$", re.M)
NUMBERED = re.compile(r"^\d+\.\s", re.M)
# 批评条目：「1. 」编号，或「**① …**」圈号加粗标题
CRITIQUE = re.compile(r"^(?:\d+\.\s|\*\*[①-⑳])", re.M)
QUOTE = re.compile(r'^>\s*\*"', re.M)
TABLE_ROW = re.compile(r"^\|.*\|\s*$", re.M)
SPECIFIC = re.compile(r"\d|多少|几[个次步条位种轮天]|百分之|阈值|参数|公式|哪[个一几]|什么模型")


def sections(text: str) -> list[tuple[str, str]]:
    """按二级标题切分，返回 [(标题, 正文)]。"""
    marks = list(H2.finditer(text))
    out = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        out.append((m.group(1).strip(), text[m.end():end]))
    return out


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"✗ 读不到文件：{path}")
        return 2
    text = path.read_text(encoding="utf-8")
    secs = sections(text)
    errors: list[str] = []
    warns: list[str] = []

    # 1. 必备章节 + 顺序
    found: dict[str, int] = {}
    for name, pat in REQUIRED:
        idx = next((i for i, (h, _) in enumerate(secs) if re.search(pat, h)), None)
        if idx is None:
            errors.append(f"缺少必备章节「{name}」")
        else:
            found[name] = idx
    order = [found[n] for n, _ in REQUIRED if n in found]
    if order != sorted(order):
        errors.append("必备章节顺序不对，应为：" + " → ".join(n for n, _ in REQUIRED))

    def body(name: str) -> str:
        return secs[found[name]][1] if name in found else ""

    # 1b. 失败模式：可以单列，也可以合并进局限 / 批判（只提醒）
    if not any(re.search(r"失败模式|局限", h) for h, _ in secs):
        warns.append("没有标题含「失败模式」或「局限」的章节；如果论文的失败分析写在实验节里，请确认已覆盖")

    # 2. 至少一条英文原文引用
    if not QUOTE.search(text):
        errors.append('没有 `> *"English"*` 格式的原文引用')

    # 3. 批判性分析：「我自己补的」≥ 3 条
    crit = body("批判性分析")
    if crit:
        mine = re.split(r"^###\s+.*我自己补", crit, maxsplit=1, flags=re.M)
        if len(mine) < 2:
            errors.append("批判性分析里没有「我自己补的」小节")
        else:
            rest = re.split(r"^###\s", mine[1], maxsplit=1, flags=re.M)[0]
            n = len(CRITIQUE.findall(rest))
            if n < 3:
                errors.append(f"「我自己补的」只有 {n} 条编号批评，至少要 3 条")

    # 4. 谱系必须有表格
    lineage = body("谱系")
    if lineage and len(TABLE_ROW.findall(lineage)) < 3:
        errors.append("谱系一节没有表格（至少表头 + 分隔行 + 一行数据）")

    # 5. 自测题：数量 + 具体度（只提醒）
    quiz = body("复习自测题")
    if quiz:
        qs = [NUMBERED.sub("", l, count=1) for l in quiz.splitlines() if NUMBERED.match(l)]
        if len(qs) < 10:
            warns.append(f"自测题只有 {len(qs)} 道，建议 12 道左右")
        if qs:
            spec = sum(bool(SPECIFIC.search(q)) for q in qs)
            if spec * 2 < len(qs):
                warns.append(f"自测题里只有 {spec}/{len(qs)} 道问到数字或机制细节，要求至少一半（启发式判断，请人工复核）")

    # 6. 速查表要有表格
    table = body("核心数字速查表")
    if "核心数字速查表" in found and len(TABLE_ROW.findall(table)) < 3:
        errors.append("核心数字速查表不是表格，或是空表")

    for w in warns:
        print(f"⚠️ {w}")
    if errors:
        print(f"✗ 结构有 {len(errors)} 处缺项：")
        for e in errors:
            print(f"  · {e}")
        return 1
    print("✓ 结构齐全：必备章节、顺序、原文引用、批评条数、谱系表格、速查表都在。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
