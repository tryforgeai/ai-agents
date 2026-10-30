# Week07 实操记录 · Workshop 与 Genie’s Exam

状态：2026-10-29 建模板，**尚未运行**。课程来源：lesson plan 印刷 pp.10–13。不提前填写实验答案。

## 环境与证据

- 日期 / 搭档：
- kit 下载日期 / 版本 / 本地路径：
- 模式：recorded replay / live（勾选；回放不是本次 live 结果）
- task model / reflection model / judge：
- seed / temperature / 预算：
- README 启动命令：取得 kit 后填写
- 导出位置：`exports/`；截图：`uploads/`；不要记录真实 key。

## Harrison’s Workshop

核心顺序 **2 → 4 → 7 → 9 → 10**。Bench 2 最终 prompt 保留给 Bench 10；Bench 10 等老师解锁。13:35 前导出全部记录，不删除失败版本。Workshop 无分数/排名，记录自己的判据。

| Bench | 讲义标题 | 课前状态 |
| --- | --- | --- |
| 1 | The Clock That Already Keeps Time | 未开始 |
| 2 ★ | Many Clocks in One Case | 未开始 |
| 3 | The Restless Hand | 未开始 |
| 4 ★ | Write Down Why | 未开始 |
| 5 | Three Turns of the Screw | 未开始 |
| 6 | The Losers’ Ledger | 未开始 |
| 7 ★ | The Specialist on Example 17 | 未开始 |
| 8 | Two Watchmakers | 未开始 |
| 9 ★ | Which Is Better? | 未开始 |
| 10 ★ | The Sea Trial | 等老师解锁 |
| 11 | The Steam Drill | 13:35 集体演示 |

### 每站复制此模板

- Bench / 时间：
- 预测 seed 会错在哪里：
- seed 输出证据：
- 我们判断好坏的一句话：
- 人手写的修改及动机（保留每个版本）：
- 输出发生了什么变化 / 哪个样本变差：
- 接受、拒绝或仍不确定，为什么：
- 14:30 debrief 给它的概念名：
- 导出文件 / 截图：

### Steam Drill 观察

- 机器与我们手工过程的相同点：
- 不同点与代价：
- 是否遗漏了我们认为不能改变的规则：

带回问题：**我们究竟怎样判断“更好”？**

## Genie’s Exam

核心顺序 **A1 → A3 → B1 → C1**。同一搭档；自写改动由人完成。界面分数是 examiner 的判断，不是团队成绩。预录结果与 live run 分开记录。

| Wing | 门 | 状态 |
| --- | --- | --- |
| A · Metric | A1 Twelve Words ★；A2 The Magic Words；A3 Out of Ten ★；A4 The Board’s Rule | 未开始 |
| B · Data | B1 Tuesday’s Child ★；B2 The Answer Key；B3 The Question Nobody Set | 未开始 |
| C · Tether | C1 The Careful Clause ★；C2 Pinned | 未开始 |
| Locked | The Examiner’s Answer | 等 debrief |

### 每门复制此模板

- 门 / 时间 / replay 或 live：
- 任务真正要什么：
- 评分规则实际上奖励什么：
- 高分但行为不好的证据（如有）：
- 人工改了什么：metric / data / tether / 其他：
- Genie 下一次输出和分数：
- 是否解决原问题 / 是否出现新问题：
- 一句话教训及证据路径：

带回问题：**我们的考试实际上奖励了什么？**

## 后续 TA session 与优化实验（待开展）

- [ ] 补完非核心 benches / doors。
- [ ] 保存 feedback、selection、holdout 的版本和划分，避免数据泄漏。
- [ ] 固定 baseline、预算、模型和 judge；记录 score + 可操作 feedback。
- [ ] 明确不可编辑规则与执行端校验。
- [ ] 冻结 winner 后评估 holdout，预先约定多 seed 与关键 slices。
- [ ] 人工检查 intron；修改后作为新候选重新评估。
