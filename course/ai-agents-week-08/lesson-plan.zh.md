# Week 08 听课速览（2026-11-08）

**The Genie's Bazaar — what prompt optimization can, and cannot, do**（讲义 30 页，Asif Qamar，first draft 2026-11-08）
📖 完整学习笔记：[lesson-plan-精读.zh.md](lesson-plan-精读.zh.md)

> **An optimizer can only change what goes into the prompt. It cannot change the weights.**
> 先判断缺的是**信息**、**知识**还是**能力**，再决定买哪种药。

## 时间线（排灯节，11:15–17:00，没有客座讲座，也没有 Speakeasy）

| 时间 | 环节 |
| --- | --- |
| 11:15 | Deep dive 收尾：GEPA、MIPROv2、记分板 |
| 13:00 | 百家饭午餐 |
| 13:45 | **Stall 1** Hostile Registry → **Stall 2** House Taxonomy |
| 15:00 | **Door A** Library →（有时间）**Door B** Gymnasium |
| 15:30 | Debrief：信息还是能力？ |
| 16:15 | Owl of Minerva（有时间才做） |

## 一张表记住全天

| | 缺什么 | 预期赢家 | 一句 lesson |
| --- | --- | --- | --- |
| Stall 1 Registry | 信息：API 的真实行为 | GEPA | 证据通过反馈句到达优化器 |
| Stall 2 Taxonomy | 信息：说不出口的规则 | MIPROv2 | 示例能装下文字装不下的东西；噪声会被忠实学走 |
| Door A Library | 知识：长尾事实 | 检索（RAG） | 事实优化不进去，检索能 |
| Door B Gymnasium | 能力：搜索 | RL（GRPO） | prompt 管格式，训练才加能力；看清跟着变的还有什么 |

## 复述题（先默写）

<details><summary>1. GEPA 和 MIPROv2 各读什么？</summary>GEPA：分数 + 一句反馈；MIPROv2：只读分数（+ 挑示例）</details>
<details><summary>2. 记分板五个 arm？</summary>naive · frontier-naive · frontier + demos · cheap + GEPA · cheap + MIPROv2</details>
<details><summary>3. 三条诚实规则？</summary>sealed test · 多个 seed · 预算相同</details>
<details><summary>4. 标准误公式？</summary>√(p(1−p)/n)；差距 < 2 SE 就分不出高低</details>

## 课前检查

- [ ] `uv sync` → `cp .env.example .env` → `uv run pytest -q`（23 passed）→ 跑 hello 那行
- [ ] **先别打开 `stalls/taxonomy.py`**，先读 30 条便签，写下自己猜的规则
- [ ] 每个 stall / door 跑之前，在 [lab-log](lab-log.zh.md) 里**写下预测**
