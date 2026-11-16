# Week 09 Lab Log · The Hundred-Million-Year Prototype + Memory Palace 一楼

搭档：
手册：`fall-agents-week-9-memory-palace-manual.pdf`（待下载）
kit：`labs/genies-memory-palace`（待下载）
规则：**做之前先写预测**；保留每次输出；先查 cue 再怪 store

## Memory Palace 设置（deck p.28）

```bash
cd course/ai-agents-week-09/genies-memory-palace   # kit 下载解压后
uv sync
uv run memory-palace          # 先读手册前两页
```

- key：已有的 OpenRouter key（默认 zero data retention）；没 key 用 **replay 模式**
- 每个房间：**Predict → Play（读 bar）→ Change（只改策略）→ Verify（十几个没见过的 case，确定性打分）**

## 玩法速查（读 kit 源码整理）

**设定**：Literal Genie 在 Fremont 家居店 **Harbor & Hearth** 当助理，老板 **Meera**。Genie 什么都不记得；**你就是 harness**，只能改它看到什么，不能改它本身。

| 楼层 | 房间 | 记忆层 | 你能改 |
| --- | --- | --- | --- |
| 一楼（W9） | 🏛️ Foyer · Glass Harness | 窗口本身 | 开关哪些 band、检索放在历史前还是后 |
| 一楼 | 🌊 Flood | episodic | recency / importance / relevance 权重、半衰期、一个 cue |
| 一楼 | 👟 Shoelaces | procedural | 从 5 条 trace 写一个 ≤300 token 的 skill |
| 二楼（W10） | Desk / Two Clocks / Diary | working / semantic / 写门 | — |
| 大厅 / 壁龛 | Long Visit / Hermes | 全部 | — |

### 🏛️ Foyer（3 个 door）

- 窗口由 9 个 band 按顺序拼成：system prompt → pinned notes → skill index → tool descriptions → summary → recent turns → retrieved episodes → retrieved facts → new message；预算 4000 token
- **G1 What did it see?**：选一个 turn，**先猜最大的 band**，再看 bar
- **G2 Take a band away**（要 key）：关掉 pinned notes / facts / recent turns，问只有那个 band 知道的问题（默认「What is our budget cap for the launch?」，答案在 pinned notes：$4,800）
- **G3 The bill**：切换「Retrieved bands before the history」，看 **prefix-cache 命中率**和成本。缓存价 = 1/10

### 🌊 Flood（4 个 door + Verify）

- 53 条 episode（6 个月），「现在」= 2027-03-01 09:00；每个问题取 **top 3**；默认 = 论文设置（权重都是 1，半衰期 5.8 天）；分数 = 三项 min-max 归一化后**加权和**
- **F1 Where it was**：cue 和记忆没有共同词 → **改 cue，不改权重**（cue 可编辑）
- **F2 The zombie address**：旧地址写入时 importance 更高 → importance 在写入时冻结，世界变了
- **F3 The loud week**：一条最近、很重要但无关的记忆挤掉了正确答案
- **F4 Ablate a term**：把某一项设成 0，看病症
- **Verify**：一组权重在 **12 个没见过的问题**里答对 **≥ 11 个**（cue 固定，只能调权重）

### 👟 Shoelaces

- 5 个周一的 reorder trace，每次 Meera 纠正一两条规则；**没有一条 trace 包含完整流程**
- 写一个 SKILL.md（≤ **300 token**），把 5 次纠正教的规则都写进去
- **离线检查**：按句子找关键词，共 **6 条规则**
- **在线**（要 key）：Genie 做 12 个没见过的 reorder，三种方式对比：no memory / 5 条 traces / 你的 skill；按店里的算术规则判对错，还显示每次调用的 memory token 数

<details><summary>Shoelaces 6 条规则（剧透，自己读完 trace 再看）</summary>

1. 覆盖 **4 周**销量
2. 再加上**供应商交货期**（Ember & Wick 1 周、Jaipur 3 周、Kolkata 5 周）
3. 减去**已在途**（on order）的数量，也减去现有库存
4. 向上取整到**整箱**（case pack）
5. **停产**（discontinued）的不列
6. **Jaipur** 每个品项**至少 2 箱**

</details>

<details><summary>Flood 提示（剧透）</summary>

- F1：原 cue 说「at the fair 一直倒的东西」，记忆里写的是 Diya floor lamp **wobbling**、weighted brass base → 把这些词放进 cue
- F3 / Verify：**relevance 要领头**（调高 relevance 权重）；recency 和 importance 都和问题无关
- F2：importance 太高会让旧地址诈尸 → importance 不能太重

</details>

## Worksheet

| 实验 | 我的预测 | 实际观察 | 讲义给的 lesson | 对得上吗 |
| --- | --- | --- | --- | --- |
| Prototype（11 个） | | | 遗忘 = 压缩；多数失败是检索失败；回忆 = 重写 | |
| Foyer（Glass Harness） | | | harness 在记；窗口即全部；band 顺序 = 成本 | |
| Flood | | | 三项各抓一种失败；权重 = 策略 | |
| Shoelaces | | | episodes 进，规则出 | |

## The Hundred-Million-Year Prototype（研究人脑这个已上线的 memory 系统）

规则（deck p.4）：跑在自己的记忆上，不用电脑；**先写下来**，再两人对比，志愿者向全班汇报。上午整段 ≈ 60–70 min。

讲义列出的 9 条 lesson，11 个实验课上对号入座：

| # | 实验名 | 我写的 | 搭档 / 全班 | 对应 lesson |
| --- | --- | --- | --- | --- |
（工作纸 2 页，课上纸质发放；对应关系是我的推断，takeaway 课上揭晓后核对）

| # | 实验名 | 题目 | 我写的 | 搭档 / 全班 | 对应 lesson（推断） | → agent 概念 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Three days | 今天起床后 / 上周二 / 四个周日前做的所有事；每列留下的是**哪类**东西？ | | | 遗忘就是压缩 | recency 衰减 + importance；consolidation 留 gist |
| 2 | The flood | 一个 cue 唤回了你不知道还在的记忆。cue 是什么？之前记忆在哪？ | | | 多数失败是检索失败 | 先查 cue（query）再怪 store；relevance |
| 3 | The edited narrative | 你「确信」发生过、直到被纠正的事。错误版本从哪来、为什么？ | | | 每次回忆都是一次重写 | compaction 重写 / 摘要漂移；provenance |
| 4 | The diary decision | 你给婚礼拍照，不给通勤拍照。为什么？ | | | 只写无法再生的东西 | write policy / salience gate |
| 5 | Shoelaces | 只用文字精确描述你怎么系鞋带 | | | 能力和回忆分开住 | procedural = skill library |
| 6 | Answer as-of | 职位 / 城市 / 最爱食物，分别按 2015、2020、今天回答；有哪个答案「错」过吗？ | | | 事实是区间 | valid time；invalidate ≠ delete |
| 7 | The two clocks | 晚几个月才知道的新闻，放上时间轴，需要几个时间戳？ | | | 两个时钟 | event time + ingestion time |
| 8 | Draw the world-line | 一个随时间演变的事实（咖啡、数学、友谊），横轴时间纵轴强度 | | | 事实是区间（连续演变） | 带有效窗口的边序列 |
| 9 | Evolution, correction, or contradiction? | 四组配对分类（见下） | | | 矛盾是一等公民 | supersede / tombstone / conflicts-with |
| 10 | The zombie fact | 能背出童年电话号码？最好朋友**现在**的号码呢？ | | | 复习 ≠ 有效 | 常访问 ≠ 仍为真；soft LFU 的陷阱；staleness |
| 11 | When did it end? | 给「不再信圣诞老人」「童年友谊结束」标日期 | | | 结局不打招呼就来 | 没有失效事件 → 需要 TTL / 主动过期 |

### 实验 9 配对

| 配对 | 我的分类 | 处理方式 |
| --- | --- | --- |
| "I live in Fremont" → "I live in Santa Clara" | **Evolution**（世界变了：搬家） | 关闭旧值的有效窗口，新值生效；旧的保留 |
| "Pluto is a planet" → "Pluto is not a planet" | **Evolution（定义变了）**，易被误判成 correction：2006 年 IAU 改了「行星」定义，之前说它是行星并没错 | 同上，带上 2006 这个边界 |
| "Sydney is the capital" → "it's Canberra" | **Correction**（旧说法从来就是错的） | tombstone：记「被 Canberra 取代」，再回收旧值 |
| Alice: "meeting at 3" · Bob: "meeting at 4" | **Contradiction**（两个来源同时不一致，谁也不取代谁） | 两条都留，记 `conflicts-with` + 来源；读时解决（问一下） |

Slide 结论：**naive memory 对四种情况都用同一条规则「newer wins」**。对 evolution 丢了历史；对 correction 碰巧对但没留痕迹；对 contradiction 是**随机**的（谁后说谁赢）。

## Foyer · The Glass Harness

**预测**：
1. 模型「记得」上一轮的东西，是谁放进去的：
2. 把两个会变的 band 挪到历史前面，账单变化：（讲义说 >50%）

**G1 观察（turn 15，全部 band 开）**：总共约 780 token（预算 4000）

| band | token |
| --- | --- |
| system prompt | ≈94 |
| pinned notes | ≈11 |
| skill index | ≈72 |
| tool descriptions | ≈63 |
| **recent turns** | **≈421（最大）** |
| retrieved episodes | ≈67 |
| retrieved facts | ≈32 |
| new message | ≈13 |
| summary | 0（还没压缩：773 远低于 4000 预算） |
| **合计** | **≈773** |

- 预测：recent turns 最大 → ✅ 对（421 / 773 ≈ 54%）

**对比 turn 3**：

| band | turn 3 | turn 15 | 变化 |
| --- | --- | --- | --- |
| system prompt | 94 | 94 | 不变 |
| pinned notes | 11 | 11 | 不变 |
| skill index | 72 | 72 | 不变 |
| tool descriptions | 63 | 63 | 不变 |
| recent turns | **67** | **421** | **×6.3** |
| retrieved episodes | 59 | 67 | 小变 |
| retrieved facts | 27 | 32 | 小变 |
| 合计 | ≈406 | ≈773 | |

- ⚠️ **turn 3 时最大的是 system prompt（94），不是 recent turns** → 我的预测只在对话后期成立；「哪段最大」取决于第几轮
- 🧭 早期：固定开销（system + pins + skills + tools ≈ 240）占大头 → 每轮都在为这些重复付费 → 这就是要把它们放在最前面吃**缓存**的原因（G3）
- 🧭 后期：历史线性增长，迟早超过一切 → 必须 compaction（锯齿波）
- 🧭 历史对话最占地方，而且每轮都在长 → 这就是锯齿波上升的那段；固定部分（system / skills / tools）每轮重复付费

| 配置 | band 顺序 | token | 缓存命中 | $ |
| --- | --- | --- | --- | --- |
| 默认（检索在历史后） | system→pins→skills→tools→summary→recent→episodes→facts→new | 16 条消息全程 | **64%** | **1,979** units（无缓存 4,665） |
| 检索在历史前 | system→pins→skills→tools→**episodes→facts**→summary→recent→new | 同上 | **37%** | **3,122** units（无缓存 4,665） |

- 预测：命中率明显低于 64%、成本上升 → ✅ 对
- 成本 1,979 → 3,122 = **+58%**（讲义：「the same window costs **over half as much again**」✅ 吻合）；命中率 64% → 37%
- 无缓存成本两边都是 4,665：token 总数没变，**只是顺序变了**
- 🧭 lesson：**band order is a cost decision**。稳定的放前面，每轮变的放越后越好 → Manus「KV-cache 命中率是生产 agent 最重要的指标」；也是「append, then compact」而不是每轮重建窗口的原因

### G2 · Take a band away

- 预测：关掉 pinned notes，Genie 不知道 $4,800，会说不知道或编一个数
- 第 1 次（claude-haiku-5.5，窗口 ≈786 token）：答 **「Hard cap: $4,800 for the whole launch. Covers printing, the photo shoot and freight.」** → ❌ 预测错
- 原因：「printing, photo shoot, freight」不在置顶笔记里，在**对话历史**里 → 第 8–9 条消息 Meera 亲口说过 $4,800，Genie 也复述过；第 27 条还算过余额。**同一个事实在两个 band 里都有**（冗余），关掉一个不够
- 🧭 lesson：要证明「某段是唯一来源」，得把**所有**含这个事实的 band 都关掉；也说明 pinned notes 的价值在**长对话被压缩以后**：那时历史里的原话可能被摘要丢掉，置顶笔记还在
- 第 2 次（关 pinned notes **+ recent turns**，窗口 ≈326 token）：答 **「I don't have a budget cap for the launch in what we've discussed so far.」** 并列出它能看到的东西（retrieved episodes / facts：Jaipur 灯笼、44 Osgood Road 仓库、launch day 营业时间 10–7），说都没提预算；请 Meera 把数字贴进来 → ✅ 预测前半句对（说不知道），**没有编数字**
- 🧭 Haiku 5.5 在缺信息时**拒答而不是幻觉**，还解释了「我看到了什么」→ 这正是好的 abstention（讲义 LongMemEval 的 abstention 能力）
- 🧭 窗口从 786 降到 326：recent turns 占了约 450 token；关掉它 Genie 就失去了整个早上的上下文 → 「不在窗口里 = 不存在」亲眼验证

## The Flood

**预测**：去掉哪一项会出什么病？

| 配置 | α_rec | α_imp | α_rel | 检索到了什么 | 病症 |
| --- | --- | --- | --- | --- | --- |
| 基线 | 1 | 1 | 1 | | |
| 无 recency | 0 | 1 | 1 | | 预期：不知道现在 |
| 无 importance | 1 | 0 | 1 | | 预期：淹没在琐事 |
| 无 relevance | 1 | 1 | 0 | | 预期：流畅离题 |

半衰期验算：γ = ____ → t½ = ln(0.5)/ln(γ) = ____ h

### F1 · Where it was（默认权重 1/1/1，半衰期 5.8 天）

原 cue：*What did we settle on for the thing that kept toppling over at the fair?*

| rank | id | 日期 | imp | rec | imp(n) | rel | score | 内容 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | e05 | 22 Sep 2026 | 6 | 0 | 0.5 | **1** | 1.5 | 展会上 Diya 落地灯一直晃，Dev **建议**加黄铜底座 |
| 2 | e47 | 28 Feb 2027 | 6 | 1 | 0.5 | 0 | 1.5 | Meera 要一个安静的一周 |
| 3 | e41 | 22 Feb 2027 | 9 | 0.5 | 0.88 | 0 | 1.37 | 拍摄彩排出事 |

- 答案应是 **e13**（11 月 6 日：Meera **决定**加黄铜底座）→ ❌ 不在前 3
- 🧭 只有 e05 有相关度（共同词「fair」）→ 检索到的是**问题**（灯晃、有人提议），不是**决定**；第 2、3 名相关度为 0，纯靠「最近」和「重要」挤进来 = 噪声
- 🧭 「settle on」「thing」「toppling」在记忆里都不出现 → cue 和存储用词不重合
- 改写后 cue：*What did Meera decide about the Diya floor lamp brass base?*（权重不动）
- 结果：✅ **The right memory came back.**

| rank | id | 日期 | rel | score | 内容 |
| --- | --- | --- | --- | --- | --- |
| 1 | e43 | 24 Feb 2027 | 1 | 1.74 | 已向工坊**订购**黄铜底座，3 月 1 日到货 |
| 2 | e47 | 28 Feb 2027 | 0.13 | 1.63 | Meera 要安静的一周（仍是噪声） |
| 3 | **e13** | 06 Nov 2026 | **0.97** | 1.59 | Meera **决定**加黄铜底座 ✅ |
| 5 | e05 | 22 Sep 2026 | 0.74 | 1.24 | 展会灯晃、Dev 建议 |

- e13 相关度 ≈0 → **0.97**，从前 8 名以外进到第 3
- 🧭 kit 的结论：「The memory was stored all along; the cue shared no words with it. **Rewrite the cue, not the weights.**」= 上午味噌汤实验
- 🧭 额外收获：e43（已下单、今天到货）排第一，比 e13 更新更完整，Genie 能答出「决定加底座，已订购，今天到」= 检索到的是一条**事件链**
- 🧭 仍有噪声：e47 相关度只有 0.13，却靠 recency = 1 排第 2 → 预告 F3：relevance 权重太低

### Flood Verify（12 题没见过的问题，cue 固定，≥ 11 题过关）

- 我用 kit 源码离线跑过：**默认权重 1/1/1（论文设置）只答对 5/12** → 论文的等权重在这个数据上失败
- relevance 提到 3（其余 1/1，半衰期不变）→ **11/12 过关**；同时 F2、F3 也通过
- 网格搜索里 557 组设置能过 ≥11，全部满分的共同点：**relevance ≥ 2、recency 降到 0.5**
- 🧭 = Deep dive 问题 1 的答案：**relevance 必须领头**；论文等权重失败，因为 recency 和 importance 跟问题无关，在 min-max 归一化后和 relevance 一样大，会把无关的新记忆 / 重要记忆抬进前 3（F3 的「loud week」）
- 🧭 讲义：「the weights are policy」；Practice I 的 retrieval config 也是 relevance 1.0 为基线、recency 0.7、importance 0.9 → 不同数据要用 eval 调，不能凭感觉
- 我的设置：recency 1、importance 1、**relevance 2.5**、半衰期 5.8 → **11/12 ✅ 过关**
- 唯一错题 **V07**「What did we decide to do about the Diya floor lamp?」（要求 e13 排第 1）：e43「已订购底座」3.24 > e13「决定加底座」3.06。两条相关度几乎一样（1.0 vs 0.98），e43 **更新**（recency 0.61 vs 0），所以赢了
- 再把 recency 降到 0.5 → e13 3.06 > e43 2.93 → **12/12**（离线验证过）
- 🧭 V07 问的是「**决定**了什么」，e43 是决定之后的**执行**；recency 偏向「最新发生的事」，但问题要的是「当初的决定」→ 问题类型不同，最优权重也不同，单一权重只能折中

## Shoelaces（实际）

5 条 trace 各教了什么：

| 周 | Genie 错在哪 | Meera 教的规则 |
| --- | --- | --- |
| 1/4 | 只算了 4 周；没按整箱；列了停产品 | 覆盖 4 周 + 交货期；整箱向上取整；停产不列 |
| 2/1 | 没扣在途的 24 个 | 减去 on order |
| 2/8 | 以为所有供应商都是 1 周 | Kolkata 交货 5 周 → 要覆盖 9 周 |
| 2/15 | 全对 | Jaipur 3 周 → 覆盖 7 周 |
| 2/22 | Jaipur 只订 1 箱 | Jaipur 每个品项至少 2 箱 |

参考 skill（离线检查：6/6 规则、≈170 / 300 token ✅）：

```markdown
---
name: weekly-reorder
description: Draft the Monday reorder for Harbor & Hearth from the stock table.
---
# Weekly reorder

For each SKU in the stock table:

1. Skip discontinued items; never list them.
2. Weeks of cover = four weeks of sales + the supplier's lead time (Ember & Wick 1 week, Jaipur Handicrafts 3, Kolkata Brassworks 5).
3. Target = weekly sales x weeks of cover.
4. Need = target - on hand - on order (count stock already on the way).
5. If need <= 0, do not list the SKU.
6. Round need up to whole case packs.
7. Jaipur minimum: if you order a Jaipur item at all, order at least two cases.

Reply with JSON only: {"SKU": units}, listing only SKUs to order.
```

- 离线检查结果：✅ **6 of 6 rules found; ≈170 tokens**（cover 4 周 / 加交货期 / 减在途 / 整箱 / 停产 / Jaipur 2 箱）
- ⚠️ 离线检查只看**有没有写到这些词**，不看写得对不对（页面原话：「it cannot tell whether you stated them well」）→ 真正的验证是在线 12 题
- 预测：no memory 很低；five traces 中等；your skill 最高且 token 最少
- 在线 12 题（claude-haiku-5.5）：

| memory given | right | memory tokens / call | errors |
| --- | --- | --- | --- |
| no memory | **0 / 12** | 0 | 0 |
| five traces | **12 / 12** | 838 | 0 |
| **your skill** | **12 / 12** | **170** | 0 |

- 预测部分对：no memory 很低 ✅；your skill 满分 ✅；**five traces 也满分**（我猜中等 ❌）→ Haiku 5.5 能自己从 5 个例子里归纳出规则
- 🧭 正确率打平，差别在**成本**：skill 只用 traces 的 **20%** token（170 vs 838，省 ~80%），每次 reorder 都省；也更稳（不靠模型每次重新归纳）
- 🧭 no memory = 0/12：模型再聪明也不知道这家店的私有规则（交货期、Jaipur 最少 2 箱）→ W8：缺的是**信息**，不是能力
- 🧭 = **consolidation**：episodes 进（838 token 的流水账），rule 出（170 token 的 skill）；讲义「a skill is consolidated procedure」

## Shoelaces（旧模板）

**预测**：从几个 episode 能归纳出规则？

- 输入 episodes：
- 归纳出的规则：
- 和 W3 skill 的对照：

## 下课前

- [ ] 一句话写今天的 lesson：
- [ ] 哪个实验的结果和预测不一样？为什么？
