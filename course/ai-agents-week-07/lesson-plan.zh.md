# Week 07 听课速览（2026-11-01）

**Gradient Descent for Sentences — the Workshop, the Frontier and the Tether**（讲义 32 页，Asif Qamar，first draft 2026-10-27）
原文：[uploads/fall-agents-week-7-lesson-plan.pdf](uploads/fall-agents-week-7-lesson-plan.pdf) · 📖 逐节精读：[lesson-plan-精读.zh.md](lesson-plan-精读.zh.md)

> **A prompt is a parameter — a point in a discrete space with no gradient — and prompt optimization is search over that space, steered by a pseudo-gradient written in words. The optimizer is only ever as good as the metric it is handed.**

## 时间线（五个 cycle；只有 14:30 和 19:30 固定）

| 时间 | 环节 | 内容 | 形式 |
| --- | --- | --- | --- |
| 11:00–11:05 | Orientation · 上周 Owl | W6 五行 | Deck |
| 11:05–11:25 | Orientation · 小测 | *Six Questions, One Trap* | Quiz |
| 11:25–12:00 | Orientation · 故事 | field notes + 六条 headlines + 那一句 | Deck |
| 12:00–13:35 | **Harrison's Workshop** | core：**Bench 2, 4, 7, 9, 10**；~12:30 午饭；Bench 10 等讲师；**13:35 前导出 Markdown** | 两人一组 |
| 13:35–13:45 | **Steam Drill** | Bench 11，全场一屏 | 全体 |
| 13:45–14:30 | **Genie's Exam** | core：**Door A1, A3, B1, C1** | 两人一组 |
| 14:30–17:00 | **Deep Dive** | debrief 揭晓 → 形式化 → GEPA → 纪律 → … | Deck |
| 17:00–18:00 | 🆕 **Guest lecture** | 讲义里没有，课上 deck 新增（主题待记） | 讲座 |
| 18:00– | **Deep dive, continued** | 接着讲 → field notes → 优化器配 artifact → 综合 | Deck |
| 19:30–19:50 | **Owl of Minerva** | 五行（先写自己的） | Deck |
| 20:00– | Speakeasy | 可选：code walk / paper walk | Talk |

> ⚠️ **课上实际议程（deck 首页，11:00 截图）和讲义不同**：Orientation 11:00 → Experientials 12:00 → Deep dive 14:30 → **Guest lecture 17:00** → **Deep dive, continued 18:00** → Owl of Minerva。讲义 p.5 没有 guest lecture，deep dive 被切成两段，所以 deep dive 的尾部（优化器配 artifact、综合）更可能被压缩，讲不到的部分看 Reservoir。
> Parking Board：deck 右上角的 "Park a question" 票，用手机扫 QR（局域网地址 10.0.21.16）；11:00 时还是空的（"Nothing parked yet."）。

## 11:00 复述题 —— 先默写

Tool label 必须告诉模型的五件事：

<details><summary>答案</summary>

description（whether）· schema（how）· error（what next）· contract（what a retry does）· 返回值（第五面）

</details>

## 课前检查

- [ ] `harrisons-workshop.zip`、`genies-exam.zip` 各解压到独立文件夹，按 README 一条命令能打开
- [ ] OpenRouter key 放好（无 key 也能回放预录输出）；投影时别露 key
- [ ] **不要提前打开任何 bench 或 door**
- [ ] 拿 `workshop-card.pdf`、`exam-card.pdf`
- [ ] Bench 2 的最终 prompt 要保留（Bench 10 要用）

## 六条 headlines

1. **A prompt is a parameter** —— "Take a deep breath…" 比 "Let's think step by step" 高 ~8 点（OPRO）
2. **You cannot do calculus on a sentence** —— 牛和马之间没有光滑路径（unicow）；梯度用文字写
3. **The optimizer reads your metric literally** —— Literal Genie 有了搜索引擎；introns
4. **Keep the specialists** —— 只有它答对 example 17 的 prompt 不能扔
5. **Small steps, a memory of failure, a gate** —— Harrison H1→H4
6. **Know when not to optimize** —— 72 次运行 49% 低于 zero-shot；judge 无 rubric 46.4%，有 rubric 73.8%

## Field notes 三课（= Genie's Exam 三翼）

前提：**resolution gap**，几十种风险塞在一个 prompt 里，其实是很多个问题

- **A · The thought is the metric** —— 每种风险一个 F_β 旋钮
- **B · The grunt work is the data** —— 一条错 demo = 一条错误教训；one blessed set
- **C · The insurance is the tether** —— 规则和定义不可编辑；"A regulator does not grade on a curve"

## 两个带回 debrief 的问题

- Workshop：***How did you decide "better"?***
- Exam：***What did your exam actually reward?***
