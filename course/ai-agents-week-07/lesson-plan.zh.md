# Week07 听课速览（课前版）

来源：[lesson plan](uploads/fall-agents-week-7-lesson-plan.pdf)，2026-10-27 初稿，印刷 pp.1–13、25–27。整理于 2026-10-29。下面是课程计划，不是课堂实录。

## 本周在解决什么

前几周是人手写 prompt、skill、tool description。本周把这些文本当参数，交给搜索循环改写；模型权重保持不变。最重要的变化是先回答“什么叫变好”，再决定如何让机器优化。

三个抓手：数据决定机器学到什么；metric 决定它追什么；tether 把不能改的规则锁住。先拆清多个问题，再优化，避免一个巨大 prompt 把不同任务的错误混在一起。

## 时间安排（照录课程时间，时区以 portal 为准）

| 时间 | 内容 | 带走什么 |
| --- | --- | --- |
| 11:00–11:05 | Week06 Owl 复习 | 上周五句主线 |
| 11:05–11:25 | Six Questions, One Trap | 回忆检查，不是预先知道题目 |
| 11:25–12:00 | 企业案例、六个 headlines | 参数、离散搜索、指标、专家、多轮改进、何时不优化 |
| 12:00–13:35 | Harrison’s Workshop，两人一组 | Bench 2/4/7/9/10；约 12:30 边做边吃；结束前导出 |
| 13:35–13:45 | Steam Drill | 全班看 Bench 11，不需要自己操作 |
| 13:45–14:30 | Genie’s Exam，同一搭档 | A1/A3/B1/C1；审视评分究竟奖励了什么 |
| 14:30 起 | Deep Dive | 体验复盘、形式化、GEPA、评估纪律、方法选择 |
| 19:30–19:50 | Owl of Minerva | 老师揭晓前先写自己的五句话 |
| 20:00 后 | 可选 Speakeasy | Parking Board、代码或论文 walkthrough |

本周日推定为 2026-11-01；当天洛杉矶结束夏令时，跨时区课程时间请以 portal 的当地时间显示为准，不沿用固定 UTC 偏移。

## 课前材料与安装

- 两套 kit：`harrisons-workshop.zip`、`genies-exam.zip`。各自独立目录，启动命令和 OpenRouter 配置看各 README；lesson plan 没给具体命令，当前不编造。
- 没 key 也能看预录运行；自写修改触发小规模 live run 才需配置 key。
- 只验证两个首页能打开，不提前打开 bench 或 door；本次没有下载或运行它们。
- 讲义明确周日无需额外安装 Deep Dive 的代码环境，实际运行在周二/周四。
- 补拿 `fall-agents-week-7-reservoir.pdf`、`workshop-card.pdf`、`exam-card.pdf`。
- Week06 kit 在 10 月 26 日前下载的应更新；讲义说 Door 1 的验证补了“提出 store credit 后等待用户回复”的情况。
- No Castle Without Walls 是上周自学材料，本周 TA session 会澄清。

## 实验纪律

这是讲义规定的学习流程：修改由人手写；chatbot 可以点评，不代写下一版实验 prompt。Workshop 不显示分数、无团队排名；保留失败版本，不整理掉历史。Bench 10 等老师信号，Bench 11 和 Exam answer 不提前解锁。

Workshop 每站：先预测 → 跑 seed → 读完输出 → 口头说为什么更差/更好 → 按本 bench 要求操作 → 记录。

Exam 每门：读任务与评分规则 → 看优化器已有的 prompt/输出 → 判断分数是否值得信任 → 人工选或写一项改动 → 看下一轮。

**14:30 带回两句话：**

1. 我们如何决定“更好”？
2. 我们的考试实际上奖励了什么？

## 课前回忆题（自拟，不是老师 quiz 原题）

1. Week06 的 description 和 server-side 检查各能保证什么？
2. 为什么模型拒绝读 `.env` 不等于脱敏函数经过测试？
3. 一个 prompt 分数从 0.70 到 0.75，至少还需哪些信息才能说变好了？
4. 数据错误、评分错误、能力不足，分别应该修哪里？
5. 自动改写退款 skill 时，哪些规则不能交给搜索过程改？
