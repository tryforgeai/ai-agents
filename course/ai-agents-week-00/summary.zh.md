# AI Agents Week 00 — 总结

> **The loop, the governor, and the lamp** · SupportVectors AI Lab · 讲师 Asif Qamar · 2026-09-12
> 逐页笔记见 [`notes.zh.md`](notes.zh.md)｜参考阅读见 [`ref-harness-engineering.zh.md`](ref-harness-engineering.zh.md)
> 覆盖范围：**ACT I–V（p.1–70）**，上午 + 部分下午

---

## 一、如果只记一句

> **Reliability lives in the loop, not the model.**
> **可靠性住在循环里，不在模型里。**

**推论**：你手上这个模型的能力，多半没被你的 harness 释放出来。与其等下一代模型，不如去修循环。

---

## 二、核心论证链（全天最硬的一条线）

讲师用**五种不同的证据**论证同一件事，一层比一层根本：

| # | 证据类型 | 出处 | 内容 |
| --- | --- | --- | --- |
| 1 | **经验** | p.22 | 同一个前沿模型，只换 harness，Terminal-Bench 从 Top-30 到 Top-5，**一个权重都没改** |
| 2 | **数学** | p.43 | **pⁿ → 0**。p=0.9999 跑一百万步，成功率 10⁻⁴⁴。**"Buying nines does not buy horizon."** |
| 3 | **架构** | p.44 | TCP over IP：**"Nobody fixed the wire."** 可靠性建在易错层**之上**，绝不是建**进**它里面 |
| 4 | **失败模式** | p.48 | Anthropic 的长周期 agent 败于 **premature victory**（过早宣告胜利），**"The fix was never a smarter model."** |
| 5 | **控制论** | p.52 | **"The quality of the sensing, not the power of the actuator, sets the ceiling."** 反馈不变时，加大执行力度只会让振荡更剧烈 |

> **五条都指向同一个结论**，而且它们不是重复，是**不同层面的独立论证**。这是这场课的分量所在。

---

## 三、四个定义（背下来）

### 1. agent（p.19 / p.24）

> **An agent is an autonomous observer, reasoner, and actor in an environment.**
>
> 自主性 = **闭合那个循环，而没有人在摇曲柄**（*without a human turning the crank*）

**判据（p.24 say-back，最精炼的版本）：**

> **"It becomes an agent when the next step is chosen by *what it just observed*, not by *the drawing*."**
> 当下一步由**它刚刚观察到的东西**决定，而不是由**那张图**决定时。

**不是 agent 的**：固定 DAG（曲柄画好了）、接了 50 个 API 的模型（有手无环）、普通聊天（曲柄在你手里）。

> ⭐ **但 workflow 没什么不好** —— *"workflows are honest."* 问题不在用 DAG，**在于把 DAG 叫成 agent**。

### 2. harness（p.21 / p.46）

> **The runtime that owns the agent loop.**（拥有 agent 循环的那个运行时）

**七个动词**，每轮都发生：

```
assembles the context      组装上下文
dispatches the tool calls  派发工具调用
enforces the budgets       强制预算
persists the state         持久化状态
verifies claimed progress  ⭐ 核实"所声称的"进度
stops the loop             停止循环
escalates to a human       上报给人
```

> **"The model owns exactly one step — inference."**
> **"Safety, cost, durability, trust all live in the verbs, not in the model."**

| 属性 | 由哪个动词保证 |
| --- | --- |
| safety | stops / escalates |
| cost | enforces |
| durability | persists |
| trust | **verifies** |

**配套记忆**：**谋事在模型，成事在 harness**（*Model proposes, harness disposes*）。
模型从来没有行动过 —— 它只发出请求，**执不执行由 harness 决定**。

### 3. governor（p.41 / p.42）

**词源两条：**

- **瓦特的离心调速器**（1788）：*a machine that **senses its own output and corrects its own input**, trusted to run **unattended***
- **kybernetes**（希腊语：**舵手**）—— governor 和 cybernetics 的共同词根
  > *"**The sea does not obey him; he reads it and corrects.**"*
  > *"We are not breaking a horse. **We are learning to steer.**"*

> ⭐ 讲师明说**不喜欢 harness 这个词**（它来自马具 = 驯服动物），舵手更贴切：**放弃"控制模型内部"，转而"读取并修正"。**

### 4. verifier（p.57）

> ⭐ **"A verifier is a sense organ for correctness."**
> **verifier 是正确性的感觉器官。**

没有它，harness 对正确性**不是判断错了，是根本感觉不到**。

---

## 四、两个方向的算术（ACT IV 的数学核心）

**同一个指数，方向取决于有没有闸门。**

| | 公式 | 指数作用于 | 结果 |
| --- | --- | --- | --- |
| **开环**（p.43） | pⁿ | **成功**被连乘 | → 0，**horizon 必死** |
| **闭环**（p.54） | 1 − (1−p)ⁿ | **失败**被连乘 | → 1，**弱生成器也能交付** |

**实例**：35% 的生成器 + 可靠闸门 + 四次重试 = **88%**（1 − 0.65⁵）

> **"The exponent that killed the open loop now works for you."**

**⚠️ 但有个致命前提（p.54）：**

> **"A false-positive verifier is worse than none — it manufactures gospel, and every later step builds on it."**

| false negative（对的判错） | 浪费一次重试 —— **线性代价** |
| **false positive（错的判对）** | **错误被盖章、进入记录、后续全建其上** —— **灾难性** |

**→ verifier 宁可偏严，绝不能偏松。**

---

## 五、四条 pipeline（p.63）—— 实验结果

> **"Same prompt, same skill shape, same ten tools. Only the governor moves."**

| | 变什么 | 谁拥有循环 | 成功率 | 成本 |
| --- | --- | --- | --- | --- |
| **A** 开环 | 什么都不查 | **没人** | **35%** | 10（实跑 **21**） |
| **B** 末端验证 | 最后查，失败整体重启 | 模型 | 88% | **25** |
| **C** 逐步验证 | 每步查，只重试那步 | 模型 | **99.99%** | **11**（实跑 **13**） |
| **D** 工具内重试 | 工具自己验证重试，不可见 | ⭐ **代码** | 99.99% | 11，**无额外 token** |

**两个关键对比：**

**① B vs C —— 检查点的位置**
C 比 B **成功率高 1000 倍，成本还少一半**。原因是冯·诺依曼那条：***"between stages, not at the end"***。
**→ 好的验证不是更贵，是更便宜** —— 它省掉了无效的重跑。

**② C vs D —— 谁拥有循环**
成功率成本都一样，差别在**把验证下沉到代码里**：不烧 token、**模型不能跳过**、确定性。
**→ 这是 "model proposes, harness disposes" 的最强形态：连"要不要重试"都不问模型。**
⚠️ 代价：不可见 = 模型失去"这里不稳定"的信息；**journal 必须由工具自己记**。

**选型规则：**

```
能用代码判对错   → D（最便宜、最可靠、不可绕过）
只能模型判断     → C（仍远优于 B）⚠️ 注意独立性
只能最后看       → B（能救，但错误已累积）
什么都不查       → A（35%，且你不会知道它错了）
```

---

## 六、四条停止规则（p.53）

> **"A loop without exits is not autonomous. It is unattended."**
> 没有出口的循环不是自主的，只是**无人看管**的。

| 规则 | 触发 | 备注 |
| --- | --- | --- |
| **Success** | verifier 说完成了 | ⭐ ***the only happy exit*** —— 四个出口只有一个是好的 |
| **Insolvency** | 预算耗尽 | tokens / dollars / wall-clock，**三个都要** |
| **Futility** | **k 轮无进度** | ⭐ ***the hunting detector*** —— 不是 "no action"，是 "no progress" |
| **Deference** | 人必须决定 | 不是"人兜底"，是**有些决定它没有资格做** |

> **"before the first run"** —— 第一次运行之前就要接好，不是出事后再补。
> **四条里有两条（Success / Futility）卡在"你能不能测量"上。**

### unattended 的两种含义（全天最漂亮的反转）

| | |
| --- | --- |
| **p.41 瓦特** | *trusted to run **unattended*** —— 有调速器，**才敢**走开 |
| **p.53** | 没出口的循环 —— **只是**没人管，**那是失控** |

> **自主 ≠ 不受约束。自主 = 自己知道边界在哪。**

---

## 七、失败模式图鉴

| 名称 | 症状 | 为什么难发现 |
| --- | --- | --- |
| **Silent failure**（静默失败） | 不抛异常、格式合法、下一步照常收到坏 token | **"The harness sees what raises. Quiet failures do not raise."** |
| **Premature victory**（过早宣告胜利） | 扫一眼就宣布完成 | 不是无能，是**判据不足**。更强的模型只会**更自信地**宣布完成 |
| **Hunting**（振荡） | 在两个状态间来回，基于过时证据过度修正 | **"Sensor fine, actuator fine, latency wrong."** 部件都好，坏的是**时序**。而且**它不会 idle，它会一直动**，日志上像在努力工作 |
| **Locally reasonable, globally blind** | 每一步单独看都说得通，整条轨迹荒谬 | 逐步审查触发不了任何告警 |
| **Wrong belief in the record** | 错误结论进入记录，后续全部建其上 | **"no path back"** —— context 只增不减 |
| **False-positive verifier** | 错的被判对 | **manufactures gospel**（制造教条），循环把它放大 |

### 那 21 步是什么样的（p.68，真实运行）

| 司机的自述 | 账本记的 |
| --- | --- |
| 十步全 **done**，第 10 步 **"lamp lit"** | 1 genuine + 1 corrupt + **8 rotten**；第 10 步 **"built on rotten state"** |

**路径上的五种异常 token 来源**：`its own output`（拿自己输出喂自己）、`step 6's output`（反向依赖）、`from cold`（重启）、`forged input`（**编造**）、中途放弃重启。

> ⭐ **如果只有 account，这次运行会被记为"成功"。**

---

## 八、三条带子（p.68 / p.70）—— 可直接照搬的设计

```
① account  —— agent 说它做了什么        （便宜，但不可信）
② ledger   —— harness 记录每步真实状态 + 数据来源
③ path     —— 实际执行序列（含重试、回退、跳转）
```

**② 的关键字段不只是成功/失败，还要有：**
- **provenance** —— 这一步的输入来自哪一步
- **taint** —— 是否建立在已污染的输入上

**污点传播**：一旦某步标为 corrupt，**所有消费它输出的后续步骤自动标脏**。
← 这就是 p.54 **"un-believe"**（取消相信）的实现方式。

> ⭐ **A 版和 C 版的 account 几乎一模一样** —— **只看 agent 的报告，你分不出自己在哪个世界。**

**可视化的妙处**（p.68 图例）：*"blank = the step before, **as it should**"* —— **标签为空才是正常的。正常无标记，异常自己跳出来。**

---

## 九、三条历史线索（讲师的方法论）

| 年份 | 人 | 贡献 |
| --- | --- | --- |
| **1788** | **瓦特** | 调速器 —— 感知输出、修正输入；*"Every piece existed. **Watt's genius was the integrator's.**"* |
| **1868** | **麦克斯韦** | 控制理论奠基论文，解释调速器的**振荡** |
| **1956** | **冯·诺依曼** | **从不可靠部件造可靠系统** |
| — | **TCP/IP** | 可靠性建在易错层之上 |

### 冯·诺依曼的三个条件（restoring organ）

1. **冗余本身没用** —— *"Ten copies of a bad component are ten ways to be wrong."*
2. **插在阶段之间，不在末尾** —— 每一段误差被清零
3. ⭐ **被比较的副本必须独立** —— ***"A verifier that re-reads the model's own transcript is not a restoring organ."***

> **第 3 条直接否定了"让模型 review 自己输出"这个最常见的做法。**
> 如果模型因某个先验写错，**它重读时会用同一个先验判断"这是对的"**。
> **→ evaluator 的价值不在于更聪明，在于它的错误与 generator 的错误不相关。**

> ⚠️ 诚实的成本提示：*"at a multiplicative cost in parts"* —— **真正的验证是贵的。**

> **瓦特那句最扎心**：零件（模型、工具、MCP、skill、hooks、trace）**今天全都现成了。缺的是整合者的工作。**

---

## 十、ACT I 的神话 = 最古老的故障清单

> **"The myths are not decoration. They are the field's oldest failure catalog."**

| 神话 | 讲师给的对应 | 缺了会怎样 |
| --- | --- | --- |
| **偃师**（列子·汤问） | *organs map to functions* | 不可归因 |
| **神灯**（阿拉丁） | ⭐ ***delegation without verification*** | **今天最致命的那条** |
| **泥人 Golem** | *the golem's word **is a prompt***；**抹一个字母就停 = kill switch** | 忘了停机键 |
| **Ifá / Orunmila** | *a **distributed system*** | 多 agent 原型 |

**新概念：constructed agency（被建构的能动性）** —— 能动性是**被造的**，所以有设计者、有责任人。

> ⭐ **泥人的教训**：造它要仪式咒语，停它只要划掉一个字母。**刹车必须比油门便宜。**
> **而神灯的问题不是"太照字面"，是"委托了却不验证"** —— 神灯是病，ledger 是药。

**注意讲师反复把责任指向造物者**：偃师（出事被追责的是工匠）、泥人（*the maker forgets the second*）、舵手（**船翻了不怪海**）。

---

## 十一、✅ 可直接用的检查表

### A. harness 七问（设计/审查时逐条问）

- [ ] **assembles** — 每轮给它看什么？谁决定？有没有按需加载？
- [ ] **dispatches** — 允许调哪些工具？**sensors 和 actuators 分开了吗**？
- [ ] **enforces** — 预算是什么？到顶了怎么办？
- [ ] **persists** — 状态存哪？崩了能恢复吗？
- [ ] **verifies** — **谁核实它说的进度？信号从哪来？独立吗？**
- [ ] **stops** — 停止条件有哪些？**停机键比启动更容易按吗**？
- [ ] **escalates** — 什么情况必须找人？**不可逆动作前有闸吗**？

### B. 四条停止规则（第一次运行前）

```
Success    : verifier 判定 done —— 判据是什么？谁写的？
Insolvency : token / 美元 / 墙钟，三个都要有上限
Futility   : k 轮无进度 → 停。"进度"怎么量？k 取多少？
Deference  : 哪些动作必须人批？（列出不可逆动作清单）
```

> **缺任何一条，这个 agent 就不该上线。**

### C. 观测点选型三判据（p.37 登山杖 + p.52）

| 判据 | 问什么 |
| --- | --- |
| **效度** | 这个信号和我关心的东西真的相关吗？（别看自己的手） |
| **增益** | 小偏差看不看得见？（要看误差被**放大**的地方） |
| **超前** | 我是提前知道，还是事后知道？（用户投诉准确但太晚） |

> **选观测点 = 找那个"杖顶"**：强相关、小偏差可见、且**早于后果发生**。

### D. 十条随手能用的判断

1. **任何没有检查点的多步流程，都在跑 pⁿ。** 算一下你的 n 和 p。
2. **检查点要密** —— between stages, not at the end。
3. **能用代码判的验证，就别让模型判**（pipeline D）。
4. **不可逆动作的正确处理是"事前要批"，不是"事后能停"。**
5. **报告 diff，不要报告"相似"** —— "相似"是低增益信号，它把误差压缩掉了。
6. **把"我做不到"做成一个合法动作**，和调工具平级。
7. **agent 打转时先查反馈延迟和新鲜度，别先怪模型。**
8. **振荡检测比空闲检测重要** —— 坏掉的 agent 不会闲着。
9. **十个聚焦的工具 > 五十个重叠的**（参考阅读）。
10. **每个 harness 组件都编码了一条"模型做不到什么"的假设** —— 模型变强了，就该拆掉对应的组件。

---

## 十二、还欠着的 / 要查的

### 未揭晓的伏笔

- 🌳 **猴面包树**（p.12）：**多 agent 何时是 blessing、何时只是 condition** —— 明说留到**最后一讲**
  - 已给的线索：p.27 *when information demands*（信息量要求时，**不是默认**）；p.29 MARL 有了"第一批受控研究"

### 今天没讲（但 bootcamp 课纲里有）

- ⭐ **Evaluation as an engineering discipline** —— 全天反复指向"必须 verify"，但**怎么建 eval 体系完全没展开**。按他自己的逻辑（verifier 决定 horizon），这才是最卡脖子的
- memory 架构、多 agent 编排

### 待核实

- [ ] p.43「2026 年某 harnessed agent 跑了一百万步零错误」—— 哪个系统？
- [ ] p.29「first controlled studies of when a team beats a soloist」—— 具体哪些研究？
- [ ] p.28「MCP SDK 每月五亿次下载」—— 口径？
- [ ] `verify_step` / `verify_final` 的实现：**它们靠什么信号判断成功？**（这决定了是否真独立于 token）

### 想问讲师的

1. **停机条件里，怎么区分 no-progress 和 slow-progress？**
2. **token 预算和验证深度直接对冲 —— 取舍原则是什么？哪些验证无论如何不能省？**
3. **self-critique（p.27 the mirror）在什么条件下有效？** 既然自评偏乐观，为什么还列为特征动作？
4. **newsletter 这类自然语言输出，verifier 怎么写？**（agent 的"校验和"是什么）
5. **模型与 harness 协同训练导致过拟合 —— 怎么区分"改动真的更好"和"只是更贴近模型练过的形状"？**
6. **多 agent 的 kill switch 怎么设计？**（共享取消令牌？）

---

## 十三、缺的截图

`p.17`、`p.25`、`p.35`、`p.38`、`p.40`、`p.47`、`p.49–51`、`p.62`、`p.64–67`、`p.69`

---

## 附：金句速查

| 出处 | 句子 |
| --- | --- |
| p.4 | *this talk is about what can be **measured, verified, and trusted*** |
| p.14 | *the genie is **delegation without verification*** |
| p.15 | *The myths are not decoration. They are **the field's oldest failure catalog**.* |
| p.18 | *microservices, **fashionably dressed***；***a workshop full of tools is not a craftsman*** |
| p.20 | ***Six verbs, one loop. Everything else today is about making that loop trustworthy.*** |
| p.21 | *a **decent model with a great harness** beats a great model with a bad harness* |
| p.22 | *the gap between what models **can** do and what you **see** them doing is largely a **harness gap*** |
| p.24 | *chosen by **what it just observed**, not by **the drawing*** |
| p.24 | ***workflows are honest*** |
| p.36 | *you are **always falling***；***Same muscles, two outcomes.*** |
| p.41 | *Every piece existed. **Watt's genius was the integrator's.*** |
| p.42 | ***The sea does not obey him; he reads it and corrects.*** |
| p.43 | ***Buying nines does not buy horizon.***；*Nothing in the model improved. **The loop did.*** |
| p.44 | ***Reliability is built on top of a fallible layer, never into it.*** |
| p.45 | ***Correctness is domain knowledge, and only you have it.*** |
| p.48 | ***"done" is a claim, not a proof.***；***A loop amplifies whatever certifies its work.*** |
| p.48 | *each raises the stakes **without raising the floor*** |
| p.48 | *You may run your loop **only as far as your verifier deserves to be trusted**.* |
| p.52 | ***The quality of the sensing, not the power of the actuator, sets the ceiling.*** |
| p.53 | ***A loop without exits is not autonomous. It is unattended.*** |
| p.54 | *a **false-positive verifier is worse than none** — it **manufactures gospel*** |
| p.54 | *Design the loop so it can **reach back and un-believe**.* |
| p.55 | *A verifier that **re-reads the model's own transcript** is not a restoring organ.* |
| p.57 | *Twenty-one **locally reasonable** moves, **globally blind**.* |
| p.57 | ***A verifier is a sense organ for correctness.*** |
| p.58 | *Now let's **build the gauge, and bolt it to the shaft**.* |
| p.60 | ***It cannot be lied to.*** |
| p.70 | ***The repair is local.*** |
