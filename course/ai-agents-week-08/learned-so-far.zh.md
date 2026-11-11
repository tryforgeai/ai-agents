# Week08 课堂时间线

2026-11-08 建立。

| 时间 | 讲师原意 / 实际观察 | 我的理解或推断 | 待核实 / 证据 |
| --- | --- | --- | --- |
| 11:00 开场 | Deck 首页「Welcome to Week 8」 | | 截图 |
| ~11:05 | 节日问候页 → Before we begin（带电脑、门户下载 kit）→ Today's theme：Prompt optimization part 2，GEPA + MIPROv2，prompt 能改什么、不能改什么 | 主题确认是 W7 续篇，不是 Memory；今天上午短讲，下午 bazaar 动手 | 截图 ×4 |
| ~11:15 | 重放 W7 deck 的小测：Quiz 6「The skill that stayed」→ (b) | 是上周的内容，先收尾 W7 | W7 deck p.13 |
| | W7 deck Story of the Day 2/4「The grunt work is the data」→ BOARD | 一条坏示例会被忠实学走 = Stall 2 的标签噪声 | W7 deck p.18；板书待补 |
| | 提到 CO-STAR 模板 | 人手写种子 prompt 的清单；优化器在它之上搜索 | 口头 |
| | W7 deck p.35 Harrison's Workshop · Thirty years at the bench | H1→H4 = 手工 GEPA；sea trial = sealed test；有立场的天文学家 = 有偏的 judge | W7 deck p.35 |
| | 板书：p_baseline = 24/40，p_opt = 38/40，validation set = 40，SE = √(p(1−p)/n) | 差 0.35 ≈ 4 个 SE，算真提升；但 validation 也被用来挑候选，最终看 sealed test | OneNote 截图；分子有涂改待核实 |
| | 板书续：√(n p(1−p)) = √(40 · 24/40 · 16/40) | 题数单位的 SD ≈ 3.1 题；baseline 24 ± 3，38 高出约 4.5 个 SD | OneNote 截图；板上结论「≈ 3.16 → ± 3」（√9.6 实为 3.10，小笔误） |
| | 板书：噪声带 +6；24→30（SD 2.7）、24→27；n → 1000 时 24→30 | 同样的幅度，n=40 是噪声（1.45 SE），n=1000 是铁证（7.3 SE） | OneNote 截图 |
| | 板书 ②：GEPA 三份数据 D_mini / D_pareto / D_val（under the pillow）；Pareto pool S₀ → g₁ → g₂；Dominance Rule 矩阵 | D_mini = 反思小批；D_pareto = 逐题打分选候选；D_val = sealed test | OneNote 截图 |
| | W7 deck p.65 D3「Popular telling vs. the paper」：前沿不是 accuracy × brevity，而是逐个训练样本；π₃ 平均分最低但独赢 d₁₇ 所以保留 | 不按 mean 选；四个候选互不支配，全留 | W7 deck p.65（补 W7 p.60 之后） |
| | W7 deck p.69 Quiz 8 answered：D 被 A 支配而淘汰；前沿 A、B、C；父代抽样 2:2:1 → 0.4 / 0.4 / 0.2 | 平均分不参与；C 独握 i₃ 所以保留 | W7 deck p.69；题目页 p.68 未截 |
| | W7 deck p.70 Bench 7, named：独解难题的偏科候选，标量优化器会删，GEPA 留下并让它繁衍；论文消融 Pareto 抽样比 select-the-best 最多 +8.17%、合计 +6.4% | 多样性 = 跳出局部最优的出口；对应我 W7 Bench 7 的 A+B+C 合并 | W7 deck p.70 |
| | W7 deck p.71 The candy shop, relabeled：同样的支配几何，坐标轴从「糖 / éclair」换成「每道训练题」；线上的点都不丢 | 先学几何，再把轴改对名 | W7 deck p.71 |
| | W7 deck p.72 Bench 8, named：System-aware merge，按模块交叉，No Frankenprompts；+5% / 约 +2%，依赖模型；前沿有多条成熟谱系后才开 | 先保留多样性，再合并；kit 里 GEPA 没开 merge | W7 deck p.72 |
| | W7 deck p.73 GEPA vs GRPO honest numbers：平均 +6%、最多 +20%，rollout 少 35×；243–1,179 次追平 GRPO，样本效率 78×；比 MIPROv2 高 10%+，prompt 短 9.2×；Budget-matched, not asymptotic | 同预算 GEPA 赢；缺能力时改权重仍赢 = Door B 的命题 | W7 deck p.73 |
| | W7 deck p.74 The Boundary：反馈只是标量时 GEPA 优势消失；2×2（反馈 × 预算）：RL/GRPO、either wins、thin ice、GEPA；Design your failures to be legible in words | = 今天 The map 的另一种画法；--feedback minimal 就是从 GEPA 格挪到 thin ice | W7 deck p.74 |
| | W7 deck p.77 Three sets, three jobs：D_feedback burned / D_pareto pressured / D_test clean（只给赢家碰一次，3–5 seed）；优化器 × never 碰 test；偷看一次就得换新 test | = 板书 ② 的 D_mini / D_pareto / D_val；只信 test mean | W7 deck p.77 |
| | W7 deck p.79 Quiz 9 The suspiciously happy run：挑选集 +11，holdout +1；prompt 4 倍长；同家族 judge + 模糊 1–10；监管切片 −6 | 四个失败：报错集合 / prompt 膨胀 / 评委偏差 / 切片退步；唯一该报的是 holdout 的 +1 | W7 deck p.79；p.80 揭晓 ✅ 四条全对，补上 verbosity bias |
| | W7 deck p.80 Quiz 9 answered：The holdout delta, across seeds, per slice — and nothing else | 噪声底、过拟合征兆 + 啰嗦偏好、自我抬高 + 无标准、分层 + no-regress 切片 | W7 deck p.80 |
| | W7 deck p.82 When not to optimize：第 0 步无差距 / 自由文本 / metric 经不起刷 / 反思模型弱 / 只调用几百次 | 会「不用」才算会用；成本账里别忘 reflector 那一行 → Reservoir §7 | W7 deck p.82 |
| | W7 deck p.83 The tether: KL for text：锁定段落（gold，优化器不许改）；C1 精灵删了谨慎条款、编承诺；钉住守住了，但那行分全丢；Pin the outcome, and make the exam agree | prompt 版的 KL 拴绳；约束和 metric 要一致；对应 capstone 的 Guard + Verifier | W7 deck p.83 → Reservoir §9 |
| | W7 deck p.95 The unit of optimization climbs：prompt（GEPA、MIPROv2、NPO、RLMOpt）→ skill（SkillOpt、gskill、SkillNEO）→ library（SkillOS、Selm）；文字当参数、反思当步长、关卡当良知 | 同一套方法往上推到 skill 和 skill 库；p.84–94 未截 | W7 deck p.95 → Reservoir §10–12 |
| | W7 deck p.97 The map, filled：每个 Bench / Door → 机制 → 工具（step zero、反思、学习率 + 失败记忆、逐样本前沿、留出集、字面 metric、学到巧合、拒绝错标签、缰绳） | W7 整周索引；Door B2 = 今天 Stall 2 噪声标签 | W7 deck p.97 |
