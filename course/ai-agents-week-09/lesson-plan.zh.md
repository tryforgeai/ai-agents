# Week 09 听课速览（2026-11-15）

**A Garbage Collector for the Mind — Act I: What Memory Is**（讲义 37 页，W9–W10 共用）
📖 完整学习笔记：[lesson-plan-精读.zh.md](lesson-plan-精读.zh.md)

> **Memory is not storage; it is policy.** 写什么、读什么、怎么合并、忘什么。

## 今天的结构

| 环节 | 内容 |
| --- | --- |
| 上午（≈ 60–70 min） | **The Hundred-Million-Year Prototype**：11 个实验，跑在自己的记忆上，不用电脑；先写 → 两人对比 → 志愿者汇报（deck p.4） |
| 下午 | Act I 理论（给上午的体验命名）：边界、四层分类、四个操作、Smallville 打分、边界纠纷 → **Memory Palace 一楼** |
| W10 | Act II context 生命周期 + Act III 构建和治理 + Speakeasy（两个 Postscript） |

（⚠️ 讲义没写具体时间，课上补）

## 一张表记住 Act I

| 概念 | 一句话 |
| --- | --- |
| 边界 | 不在窗口里 = 不存在；memory = 窗口外可以换入的东西 |
| 谁在记 | **harness**，不是模型 |
| 四层 | working = 窗口；episodic = trace；semantic = RAG；**procedural = skill library** |
| 四操作 | write / read / consolidate / forget（没有 storage） |
| 读的账 | VoR = p·g − κ(c) > 0 才换入 |
| 打分 | recency + importance + relevance，权重全 1；γ = 0.995/h → 半衰期 ≈ 138 h ≈ 6 天 |
| 遗忘是功能 | privacy / staleness / relevance drift；Funes 什么都不忘所以不能思考 |

## 边界纠纷（各一句）

- **RAG** = 关掉写入的 memory
- **FT** 学英语，**memory** 学你的名字
- **Long-context** = 更大的书桌，不是取消硬盘
- **State** 随任务死；临时假设升格成事实 = 投毒
- **KV-cache** 在另一个海拔（W10 讲）

## 复述题（先默写）

<details><summary>1. 为什么「the model remembers」是错的？</summary>LLM 跨调用无状态，是 harness 存了事实再注入下一个 prompt</details>
<details><summary>2. 哪一层「不存在别处」？</summary>working memory = context window 本身</details>
<details><summary>3. H.M. 说明了什么？</summary>程序性记忆和陈述性记忆分开：不记得来过，但镜像画图越来越好</details>
<details><summary>4. 为什么 recency 是 soft LFU？</summary>衰减从上次访问算起，常用的不断重置时钟</details>
<details><summary>5. Importance 什么时候打分？</summary>写入时，LLM 打一次 1–10，存下来，不每次读都重算</details>

## 实验时盯住

- [ ] 每个实验**先写预测**再做（W8 的老规矩）
- [ ] Flood：失败时**先查 cue 再怪 store**
- [ ] Foyer：注意 band 顺序对**账单**的影响（W10 缓存账的伏笔）
- [ ] Shoelaces：episodes 进，规则出 = skill 是合并过的程序
