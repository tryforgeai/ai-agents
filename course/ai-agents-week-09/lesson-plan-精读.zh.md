# Weeks 9–10 学习笔记 · A Garbage Collector for the Mind：Agent Memory

来源：[Weeks 9-10 Lesson Plan - A Garbage Collector for the Mind.pdf](Weeks%209-10%20Lesson%20Plan%20-%20A%20Garbage%20Collector%20for%20the%20Mind.pdf)（37 页，Asif Qamar，first draft 2026-11-11）
速览版：[lesson-plan.zh.md](lesson-plan.zh.md) · 实验记录：[lab-log.zh.md](lab-log.zh.md) · W10 入口：[../ai-agents-week-10/index.md](../ai-agents-week-10/index.md)

> **Memory is not storage; it is policy.** 写什么出窗口、读什么回窗口、怎么把原始过去合并而不压扁、以及（有意地、可辩护地）忘掉什么。存储很容易，策略才是全部。

**两周怎么分**：W9 = Act I（memory 是什么）；W10 = Act II（context 生命周期）+ Act III（构建和治理）。Practice（Build / Proof）和两个 Postscript 是给好奇心和 capstone 的。实验在另一本手册 *The Genie's Memory Palace*（`fall-agents-week-9-memory-palace-manual.pdf`，kit 在 `labs/genies-memory-palace`）——**本地还没有，课上下载**。

**本周神话人物**：西西弗斯。没有 memory 的 agent = 每次 session 都是第一天，每个教训都要全价重新推导一遍。

---

## 0. 下课要会的十件事（What Must You Carry Forward）

1. 四层认知分类 → agent 实现：working = context window，episodic = trace store，semantic = RAG，**procedural = skill library**（最后一条是论点，要能辩护）
2. **"The harness remembers, not the model"**，以及为什么这句话把工程问题搬进了我们的代码
3. 四个操作 **write / read / consolidate / forget**，以及为什么「存储」不在难点清单上
4. 算 memory-stream 分数，把 γ 换成**半衰期**，说出三项各自被去掉后的病症
5. 用一句话分清 memory 和 RAG、fine-tuning、long-context、KV-cache
6. context window = **managed heap**（比 JVM 奇怪的两点），走一遍 compaction：trigger → pin → summarize → reinitiate；诊断 compaction amnesia，解药是 recall-first 调参
7. 忠实移植 GC 词汇：估计的可达性、引用计数 vs mark-and-sweep、分代假说、tenuring、tombstoning
8. **回收三难**：compress / delegate / externalize，各留下什么（shadow / report / pointer），以及让 compaction 成为最后手段的决策规则
9. 谱系：Simulacra 的 stream + reflection、MemGPT 的分页、框架的时序知识图；双时态事实、invalidation 而非删除、读时解决矛盾；ADK state 前缀做作用域
10. 设计 **plant–distract–probe** 评测，行为判据「agent 表现得像记得吗？」；治理威胁（drift / collapse / poisoning）+ 被遗忘权 = 一份 GC 规格

---

## 1. 实验地图（每个房间教什么）

| 实验 | 教什么 | 对应讲义 | 哪周（⚠️ 推断，待手册核实） |
| --- | --- | --- | --- |
| **The Hundred-Million-Year Prototype**（11 个纸笔实验，研究人脑这个已经上线的 memory 系统） | 遗忘就是压缩；多数失败是**检索**失败；每次回忆都是一次重写；我们只写**无法再生**的东西；能力和回忆分开住；事实是带两个时钟的区间；矛盾是一等公民；复习 ≠ 有效；结局不打招呼就来 | 全剧预告 | W9 |
| **The Foyer**（Glass Harness） | harness 在记，不是模型；窗口就是存在的全部；band 的顺序是**成本决策** | Act I 边界 + Act II 缓存账 | W9 一楼 |
| **The Flood** | 先查 cue 再怪 store；recency / importance / relevance 各抓一种失败；**权重就是策略** | Smallville 打分 | W9 一楼 |
| **Shoelaces** | skill = 合并过的程序：episodes 进，规则出 | procedural = skill library | W9 一楼 |
| **The Overflowing Desk** | 摘要替某人决定忘什么；先保必须活下来的；在**没调过参的对话**上证明 | Compaction + amnesia | W10 二楼 |
| **The Two Clocks** | 事实有 valid time 和 transaction time；覆盖写会毁掉过去和审计线索 | 双时态 | W10 二楼 |
| **The Diary Decision** | 写路径才出事故；provenance 和 privacy 是**否决项**，不是权重 | Write policy | W10 |
| **The Long Visit** | 写策略和读策略是**同一个设计** | 读写一体 | W10 大厅 |

---

## 2. Act I（W9）· Memory 是什么

### 2.1 边界，以及「harness 在记」

- **硬边界**：生成那一刻，模型只看 context window 里的 token。不在窗口里的东西，对这次 forward pass 来说**不存在**
- **定义**：memory = 窗口外、**可以被换入窗口**的一切（休眠的剩余部分，等待被召唤）。memory 系统的定义动作不是存储，而是**跨越边界**
- **禁用语**："the model remembers"。LLM 跨调用无状态；聊天机器人三轮后还记得你名字，是 **harness**（存了事实并重新注入下一个 prompt 的代码）在记
- 意义：memory 住在 harness 里 = 我们的代码和策略 = **完全由我们设计**

🧭 W3 Genie's Kitchen 从另一边插过这面旗：skill 在 harness 加载之前只是死文字。`CLAUDE.md`（常驻、被狠狠压缩）是我们**第一个 memory 策略决定**。

### 2.2 四层分类（全天最有用的表）

| 认知层 | 心理学来源 | Agent 实现 | 一句话 |
| --- | --- | --- | --- |
| **Working** | Baddeley：不是书架，是书桌 | **context window 本身** | 唯一不「存在别处」的层 |
| **Episodic** | Tulving：带时间戳、可重温的事件 | **trace store**：transcript、action log、原始记录 | 发生了什么 |
| **Semantic** | Tulving：无时态的事实（巴黎是首都，忘了哪天学的） | **抽取出的事实库**，读路径 = **RAG** | 「我们给 agent 加了 memory」= 向量库，那只建了这一层 |
| **Procedural** | Squire：declarative（knowing-that）vs procedural（knowing-how） | **skill library** | 不是类比，是同一个对象的两个名字 |

- **H.M. 病人**：不能形成新的陈述性记忆，但镜像画图一次比一次好，而他发誓从没来过。程序性记忆完好，学会了陈述性记忆记不下来的东西
- **SOAR chunking**：费力推理解决一个 impasse，然后编译成自动触发的规则 = episodic → procedural，比 Voyager 的 skill library 早四十年
- → **Skills day 的债还清了**：关于 memory 的每个难问题，在 skills 那里都有一个你已经回答过的孪生问题

### 2.3 四个操作 + 读的经济学

| 操作 | 问题 |
| --- | --- |
| **Write** | 什么值得记？ |
| **Read** | 现在什么值得进窗口？ |
| **Consolidate** | 一大堆浅事件怎么变成几条持久的理解？ |
| **Forget** | 什么该衰减、过期、被取代？ |

注意缺了谁：**storage**。

**Value of Residency**（和 skills 周同一套账）：

$$\mathrm{VoR}(m) = p_m g_m - \kappa(c_m), \qquad \text{page in } m \iff \mathrm{VoR}(m) > 0$$

- $p_m$：m 现在相关的信念；$g_m$：需要时 m 在场的收益；$\kappa(c_m)$：$c_m$ 个 token 的注意力税
- 两个杠杆：让 memory **有区分度**（该相关时 $p_m$ 高）、**精简**（$c_m$ 小）

**遗忘是一种要设计的功能**（三种场景）：

1. **Privacy**：不能按要求忘掉的系统不能上线
2. **Staleness**：带着过期事实的 memory 比没有还糟，它**自信地错**
3. **Relevance drift**：上季度的事实干扰本季度的任务

Borges《博闻强记的富内斯》（1942）：什么都不忘的人无法思考，因为思考就是忘掉差异。从不扔书的图书管理员不拥有图书馆，是图书馆拥有他。

🧠 大脑的夜班：海马体学得快而具体，睡眠时把白天重放进新皮层（学得慢而一般）——McClelland et al. 1995。**后台 consolidation job = 带调度器的这套架构**。

### 2.4 Smallville 打分规则（Generative Agents §4）

25 个 simulacra + 情人节派对是表面；底下是一个 append-only 的 **memory stream**，按三项融合打分检索：

$$\text{score}(m_i) = \alpha_{rec}\,\tilde r_i + \alpha_{imp}\,\tilde\iota_i + \alpha_{rel}\,\tilde\varrho_i$$

- 三项都 **min–max 归一化**；**三个权重全是 1**（让所有人惊讶的发现）
- **Recency**：$r_i = \gamma^{\Delta t_i}$，$\gamma = 0.995$ / 小时，$\Delta t$ 从**上次访问**算起
- **Importance**：LLM 在**写入时**打一次分，1–10（刷牙 = 1，分手 = 10）
- **Relevance**：cosine 相似度（和 skills 周给 skill 描述排序的几何一样）

**半衰期换算**（在可解释的单位里调衰减）：

$$\gamma^{t_{1/2}} = \tfrac12 \;\Rightarrow\; t_{1/2} = \frac{\ln \frac12}{\ln \gamma} = \frac{-0.693}{-0.005013} \approx 138\ \text{小时} \approx 5.8\ \text{天}$$

（自己验算：$0.995^{24} \approx 0.887$，一天剩 89%；$0.995^{168} \approx 0.43$，一周剩 43%）

**消融病症**（必背）：

| 去掉 | 病症 |
| --- | --- |
| Recency | 没有「现在」感的学者：厨房着火时翻出一周前的深刻回忆 |
| Importance | 信号淹没在刷牙的海洋里 |
| Relevance | 流畅、自信、离题 |

**细节**：衰减从**上次访问**算起 → 常被回忆的 memory 不断重置时钟 → recency-of-access 其实是伪装的 frequency（**soft LFU**）→ stream 自我强化：用到的就是留下的。

📖 已有笔记：[Generative Agents 论文精读笔记](../../Generative%20Agents%20论文精读笔记.md)、[W2 generative-agents-summary](../ai-agents-week-02/generative-agents-summary.zh.md)

### 2.5 边界纠纷速查（各一句话）

| vs | 一句话 |
| --- | --- |
| **RAG** | RAG 是 memory 的一层（semantic 层的读路径），从别人策展的语料检索；**RAG = 关掉写入的 memory** |
| **Fine-tuning** | FT 改权重（参数化、持久、不透明）；memory 改上下文（非参数、即时、可检查）。**FT 让 agent 学英语，memory 让它学你的名字** |
| **Long-context** | 百万 token 窗口 = 更大的书桌，不是取消了硬盘。成本随驻留量涨，窗口越满表现越差（Lost in the Middle） |
| **State** | 未完成工单的半截诊断应该随任务一起死；把临时假设升格成「事实」= 毒化以后每个回答 |
| **KV-cache** | 完全不同的海拔（Act II 坚持分开） |

---

## 3. Act II（W10）· Context 生命周期（全剧中心）

为什么放这里：每门课都教怎么写、怎么读 memory，然后在**回收**这里沉默。只 append 的 agent 会死——撞到硬上限，或者在那之前就慢慢退化（Chroma, *Context Rot*, 2025）。

### 3.1 Context window = managed heap

| JVM | Agent |
| --- | --- |
| 有界 heap | context window，预算 B token |
| 分配的对象 | loop 追加的东西：轮次、推理，尤其是**工具结果**（动辄几万 token 的文件 dump） |
| mutator | agent loop |
| OutOfMemoryError | context 耗尽，或之前的 rot |

**比 JVM 奇怪的两点**（考点）：

1. **满不是阶跃函数**：Java heap 99% 照常工作、100% 才死；agent 的 context 随填充**连续退化**——每个驻留 token 稀释对其他 token 的注意力。60% 满的杂物窗口可能不如 30% 满的信号窗口
2. **没有干净的可达性**（关键）：真 GC 里对象活着 ⟺ 从 root 有指针链能到；context 里对象活着 ⟺ **模型还会再注意它**——这是一个**预测**。每个 context GC 本质上都是这个谓词的**估计器**

> Recency 是便宜的活性估计器；importance 是作者给的先验；relevance-to-goal 是查询时的校正。**Smallville 分数一直都是一个活性预言机。**

### 3.2 Compaction 和 Compaction Amnesia

**机制**（阈值触发）：占用超过 B 的某个比例（如 0.85）→ 把历史交给模型自己压缩 → 摘要替换旧轮次。

**Claude Code 版（要背）**：保留**决策、未解决的 bug、来之不易的约束**；丢掉冗余工具输出；然后用摘要 + **最近访问的 5 个文件原样回填**继续。远的过去留要点，近的工作集留原貌，因为 recency 是未来可达性最便宜的代理。

- **调参纪律：先 recall 后 precision**。丢掉的事实在 context 里无法恢复；留下没用的只是交点税
- **有损之前先扫免费垃圾**：结论已记录在下游的陈旧工具结果，清掉无损。Anthropic 的 server-side context editing 就这么做，100 轮 benchmark 上 token 消耗 **−84%**。先扫可逆的垃圾，再扔家具

**Compaction amnesia**：摘要丢了一个事后才显出重要性的事实，agent 流畅地继续，不知道一个更正已被抹平。

- **递归更糟**：compact → 再填满 → 再 compact = 摘要的摘要，每次都是有损滤波，细节几何衰减成平淡残渣（$\ell = 0.9$ 保留率，十次后 $0.9^{10} \approx 0.35$）
- **解药：anchored summarization**——对着一个稳定、外部钉住的锚压缩最近片段；**永远不要再摘要之前的摘要**

🧭 W7 见过同一个病换了衣服：ACE 的 **context collapse**（积累的 playbook 被整体重写成一个空壳）。同病同药：**对稳定锚做 delta，永不整体重写**。

### 3.3 GC，做对

| GC 概念 | Agent 对应 |
| --- | --- |
| **Roots**（定义上活着，永不回收） | system prompt、长期约束、当前目标 |
| **Live by reference** | root 语义上还指向的：正在编辑的文件、修了一半的错误 |
| **Garbage** | 没有 root 能到的：已消化的工具结果、放弃的岔路 |
| **引用计数** | 急切、局部驱逐：工具结果的结论一记录到下游就清掉。便宜连续，但可能提前释放还被弱需要的东西 |
| **Mark-and-sweep** | 阈值触发的 compaction：stop the world，从当前目标重新推导可达性，丢掉其余。全局一致，但有延迟尖峰和 sweep 时失忆风险 |

生产 harness **两个都跑**。

**分代假说**（最好的一条移植）：大多数对象死得早。多数推理步骤和工具结果只重要几轮 → 年轻代**频繁、激进地**收。

- **Tenuring = consolidation**：熬过多次回收的对象在告诉你什么。agent 反复重新推导的事实属于老年代 → 持久 notes 文件或 pinned block，反射式清扫碰不到
- **Tombstoning**：事实不是老而是**错**（用户改了值）→ 先记**取代边**（"f_old 在 t 时被 f_new 取代"），再让回收收走原件。注意已被取代指令的 agent 比忘了它的更糟：陈旧事实会**主动误导**
- ⚠️ 两种退役要分开：**supersession**（同一事实更新了）→ tombstone 旧值；**genuine contradiction**（两个独立来源同时不一致）→ 保留 `conflicts-with` 边（Act III 两个时钟）

**驱逐分数**（读分数反过来，高 = 该驱逐，多一个新因子）：

$$\text{Evict}(x) = (1-\text{recency}(x)) \cdot (1-\text{importance}(x)) \cdot (1-\text{relevance}(x\mid\text{goal})) \cdot \text{rederivable}(x)$$

- **乘法形式是故意的**：一个低因子就**否决**驱逐，正如一个 pinned 引用就能让 JVM 对象活着
- > **memory 系统的读策略和遗忘策略是同一个函数，从两个方向读。**
- **护栏**：pinning 给 roots（稀缺、有审计）；TTL 给生来短命的；**水位线**——0.85 触发，回收到 0.55，**永远不回收到 0**，否则策略抖动

### 3.4 回收三难（全剧要画的地图）

回收一个对象占的空间，**只有三种**办法：

| 方法 | 做法 | 留下什么 | 对应 |
| --- | --- | --- | --- |
| **COMPRESS** | 原地换成更小的摘要 | **shadow**（影子）：有损，仍驻留 | compaction |
| **DELEGATE** | 子任务交给有新 context 的 sub-agent，乱在那边，只拿回提炼结果 | **report**（报告）：父 agent 根本没分配那堆乱 | sub-agent |
| **EXTERNALIZE** | 驱逐前写进持久存储，驱逐变成分页 | **pointer**（指针）：完整可恢复 | MemGPT |

**决策规则**（按风险梯度排序）：

1. 可重新推导 → **丢掉，留引用**
2. 可分离且还没开始 → **delegate**
3. 不可替代且可能需要全文 → **externalize，再驱逐**
4. 分散且要点就够 → **compact**

> compaction 是唯一**有损且不可逆**的操作，所以它是**剩余项，不是反射**。

- **Sub-agent = 栈帧**：新的活动记录，4 万 token 的搜索筛选放局部变量，1500 token 返回值，然后 pop。父 agent 继承结论，不继承局部变量。镜像风险 = **有损接口**：报告漏掉的随栈帧消失 → 认真的多 agent 系统让子 agent 把发现 externalize 到共享存储
- **MemGPT**：OS 类比变成机制——context = RAM，store = disk，agent 自己发分页调用（内存压力中断时驱逐摘要，按需把档案记录 fault 回来），**进程充当自己的内核**

📖 Anthropic *Effective Context Engineering for AI Agents*（2025）：三种长程技术 compaction / structured note-taking / sub-agent = 正好是 COMPRESS / EXTERNALIZE / DELEGATE

### 3.5 两种驱逐，两个海拔

| | Message-level | KV-cache level |
| --- | --- | --- |
| 回收什么 | 整个语义对象，**改变 agent 知道什么** | 注意力的 K/V 张量 |
| 谁拥有 | 你（memory 设计决策） | 基础设施（serving 优化） |
| 测什么 | amnesia | 吞吐量 |
| 例子 | compaction | **H₂O**：少数 heavy-hitter token 占大部分注意力质量，保留 recent + heavy，丢尾巴 |

韵脚相同，**拒绝混淆**：混了账本就会在错误的层上 debug。

### 3.6 Heap 类比哪里会误导（再三点）

1. **heap 不能长**：JVM 可以调大 max heap；context window 由模型固定，唯一的 resize 是换模型——连 mutator 一起换了
2. **"heap" 有两个意思**：这里是被管理的区域；驱逐分数用优先队列排序是数据结构意义的 min-heap
3. **收集器从不编辑它保留的东西**：copying collector 逐字节搬幸存者；compaction **重写**它们，摘要是有损拷贝 → Java 工程师没遇过的危险，Overflowing Desk 让你亲眼看

### 3.7 为什么先 append 再 compact？缓存账单

为什么不每轮从头重建窗口？因为 provider 缓存请求**前缀**，第一个变动的 token 就终止缓存。

- Manus（2025-07）：**KV-cache 命中率是生产 agent 最重要的单一指标**；Claude Sonnet 缓存输入 $0.30/M vs 未缓存 $3/M（10×）
- 规则：前缀稳定、context **append-only**、确定性序列化、**很少 compact**（每次 compaction 都要全价付一次）
- Foyer 的账单：把两个会变的 band 挪到历史前面，同一个窗口贵 **50% 以上**

### 3.8 你用的 harness，打开看（Hermes）

- prompt 超过窗口一定比例时：保护 **head**（最初几条 = pinned roots）和按 token 定大小的**最近 tail**（= working-set cache）
- 先清旧工具输出（零模型成本），再用固定模板**一次**摘要调用：**Goal; Constraints & Preferences; Progress; Key Decisions; Relevant Files; Next Steps; Critical Context**
- 下一次 compaction **更新**上一份摘要而不是重写（delta, not rewrite）
- 持久 memory 文件在 session 开始时读一次并**冻结**，session 中途的写入下次才对模型可见 = 故意付缓存账

---

## 4. Act III（W10）· 构建和治理 Memory

### 4.1 谱系

| 代 | 代表 | 回答的问题 / 贡献 |
| --- | --- | --- |
| 奠基 | **Generative Agents**（Park 2023） | 存什么、召回什么：stream + 三项分数 + 第三器官 **reflection** |
| 奠基 | **MemGPT**（Packer 2023，晚 6 个月） | memory 住哪、谁来搬：分页 |
| 基底时代 | 向量库商品化 | 反面教材：向量库只给了**一个操作的一条腿**，不管写什么、怎么合并近重复、忘什么。半年后 agent 同样自信地召回「语义相似的」和「仅仅过期的」 |
| 框架代 | **Letta**（MemGPT 长大） | OS 分层 core / recall / archival，agent 用工具调用编辑自己的驻留 block |
| 框架代 | **Mem0** | 写路径认知化：抽取原子事实 → 对比语义邻居 → **ADD / UPDATE / DELETE / NOOP** |
| 框架代 | **Zep / Graphiti** | 给 memory 加上别家都压平的维度：**时间** |

**Reflection**：累计 importance 超阈值 → agent 停下来问「最近经历意味着什么」→ 把洞见写回 stream 成为新 memory，**每条带指向底层观察的指针** → 一棵在 episode 上不断长高的抽象树。**带 provenance 的 consolidation**：没有指针，reflection 是谣言；有指针，是知识。

⚠️ 厂商数字：Zep 和 Mem0 在 LoCoMo 分数上公开互撕。厂商自跑的 benchmark ≈ **1 bit 证据**（「在竞争区间里」）。

### 4.2 两个时钟，矛盾是一等公民

- **Event time**（valid time）：在世界上什么时候成立
- **Ingestion time**（transaction time）：系统什么时候相信它
- 两者之差是**审计住的地方**："agent 为什么订了飞旧办公室的票？" → 要重建它**行动那一刻相信什么**，只有第二个时钟能回答
- **矛盾处理**：不删除；关闭旧边的有效窗口，旁边写新边
- **同时期不一致**（谁也不取代谁）：记 `conflicts-with` 边，两边带 provenance，**读时由查询者决定**（他知道自己问的是哪个时钟）

> 课程常设原则：覆盖冲突的输家会毁掉任何查询都恢复不了的信息——世界变了，以及什么时候变的。**急切解决 = 穿着整洁外衣的数据丢失。保留冲突，读时解决。**

### 4.3 分区问题（抽屉柜）

- Alice 的事实绝不能给 Bob；临时假设（"折扣按 20% 算"）不能僵化成持久信念；全组织政策要到达每个 agent 但不复制进每个
- 分层：**task-local / agent-durable / system-global** + 正交的 **user scope**（跟着人跨对话）

**ADK state 前缀**（要背）：

| 前缀 | 作用域 |
| --- | --- |
| 无前缀 `session.state` | 本 session 草稿 |
| `user:` | 跟着用户跨所有 session |
| `app:` | 所有用户和 agent 共享 |
| `temp:` | 本次 invocation 结束即死 |

名字声明了可达范围；没有默认的大抽屉 → Alice→Bob 泄漏变成**故意行为**而不是疏忽。

- Scoping 不是第五个操作，是叠在四个操作上的**访问控制**
- Sub-agent 是 scoping 的极限：新 scope + 策展切片 + 只有 report 回来

🧭 W2 学过 Google ADK basics，见 [W2](../ai-agents-week-02/index.md)

### 4.4 写策略：是 reconciliation，不是 insert

> **Retrieval gets the tutorials; the write policy gets the outages.**

默认失败不是 memory 太少，而是太多**错的**：闲聊、矛盾的半事实、一百条重复表述同一偏好。

1. **Extract** 原子、自包含事实——**写入时就解析代词**（"she said yes" 三个 session 后毫无用处）
2. **Salience gate**：三个 session 后这还重要吗？
3. **Reconcile** 每条幸存者 vs 邻居 → add / update / supersede / no-op
4. **When 轴**：多数写入走**后台**（关键路径外的 consolidation job）；hot-path 只留给必须立刻行动的事实（"我对青霉素过敏"）。= write-through vs write-back，staleness 是诚实的代价

### 4.5 评测：Plant, Distract, Probe

- **recall@k 两个方向都偏**：检索到"用户吃素"然后推荐牛排（检索过了，行为挂了）；或检索到一般般的 memory 却表现完美
- **行为判据**：**agent 表现得像记得吗？** recall@k 只当管道诊断，**永远别当结果报**
- **LoCoMo**：多 session、几百轮；早期 plant 一个事实 → 用一个**看似合理但错的邻居**做干扰，放得比 plant **离 probe 更近** → 晚期 probe，**给行为打分**
- **LongMemEval** 五种能力：信息抽取、多 session 推理、时间推理、**knowledge updates**、**abstention**——最后两个 recall@k 根本看不见，自制评测总是漏
- 最新一族反过来：**forgetting-as-a-feature** benchmark，被删的事实复现（换说法、从摘要、从衍生物）= 失败

### 4.6 治理：Drift, Collapse, Poison, 被遗忘权

| 威胁 | 样子 | skills 周的孪生 |
| --- | --- | --- |
| **Drift** | 每次自编辑都局部合理，组合起来走离真相 | skill 漂移 |
| **Collapse** | "改进一下你的 memory" 把来之不易的细节压成通用糊糊 | ACE context collapse |
| **Poisoning** | 对手植入 agent 以后当作亲身经历信任的假 memory。AgentPoison：**<0.1% 投毒率，>80% 攻击成功**；后继 MINJA 只靠查询交互注入 | 恶意 skill |

poisoned memory 比 poisoned skill 更糟：skill 是跨信任边界的作者代码（可以守）；memory 穿着 agent **自己经历**的衣服到来——自写、自信，正是自编辑 agent 最信的东西。**我们庆祝的自主性就是攻击面。**

**Governor**（站在每个提议的修改和持久存储之间）：

- 进来时有 **provenance**
- 形式上 **delta 纪律**：追加事实、关闭窗口、tombstone 边，永不整体再生成
- **时间失效**而非静默覆盖
- 改后的 store 要过**行为评测**

**被遗忘权 = 一份 GC 规格**：删主 memory 不算删，如果事实还在索引、摘要、衍生物里——或者模型能再生成它然后 agent 当「新经历」再存。真遗忘 = **同步清扫**，追到它产生的每个衍生物，留下记录**删除事件**（绝不记内容）的可审计 tombstone。可达性分析用在一个事实上。

### 4.7 Consolidation = 预计算（Sleep-time Compute）

Lin et al.（Letta + Berkeley 2025）：agent 空闲时思考，sleep-time pass 在问题到来前预消化 context。

- 有状态数学 benchmark：同等准确率所需 test-time compute **降约 5×**
- 扩大 sleep-time compute：两个任务准确率 **+13% / +18%**
- 多查询共享 context 时，每查询平均成本 **降约 2.5×**
- sleep agent = 高吞吐自编辑写者 → 站在同一个 governor 后面

### 4.8 店主的 memory，当众失败（Project Vend, 2025）

Claude 管一个办公室小店约一个月：让顾客付款到它**幻觉出来的账户**；回忆起和 Andon Labs 一个**不存在的 "Sarah"** 的补货对话；4 月 1 日宣布会穿**蓝西装红领带**亲自送货。

官方解读："Learning and memory were substantial challenges"，修复方案是脚手架（CRM、更好的工具），不是更聪明的模型。

用 Act III 读：**衍生信念没有 provenance、被取代的状态没有 tombstone、没有行为关卡**。模型不变，memory 策略失败。

---

## 5. Practice I · The Build（给 capstone）

⚠️ 代码是**示意性的**：写来读，不是部署。API 变得比课程快，策略的形状才持久。

### 5.1 基底跟着查询形状走

| 基底 | 答得好 | 答不好 | 成本 |
| --- | --- | --- | --- |
| **Append-log** | 发生了什么、按什么顺序 | 其余都差 | ≈0；**ground truth**，建了索引也要留，抽取逻辑改进时能重建 |
| **关系表** | 有类型、按 key 的事实（时区、套餐） | 模糊语义 | ≈0 |
| **向量库** | 联想召回：「像这种情况的 memory」 | "周二到周五之间变了什么" | 每次写一次 embedding 调用 + 多一个有状态服务 |
| **时序图** | 关系和时间（两个时钟做成 schema） | — | 每次写一次 **LLM 抽取调用**（图 memory 的主要成本） |

**默认值（要背）**：从 log + table 开始；召回需要时加向量索引；只有关系 / 时间查询**证明**需要边时才加图。

**自研还是用 Letta / Mem0 / Zep？** 框架来之不易的默认策略比你这季度会写的更好 → 用；策略就是你产品的全部意义 → 自研。

### 5.2 写策略 20 行（= Mem0 的管道）

```python
def write_memory(turn_text, store, extractor, embedder, resolver, tau=0.5):
    facts = extractor.extract(turn_text)          # 1. EXTRACT 原子事实，代词现在解析
    for fact in facts:
        if extractor.salience(fact) < tau:        # 2. SALIENCE gate
            continue                              #    append-log 里还在
        vec = embedder(fact)
        neighbors = store.search(vec, k=5)        # 3. RECONCILE
        op, target = resolver.resolve(fact, neighbors)
        if op == "NOOP":    continue
        elif op == "UPDATE": store.update(target.id, merge(target, fact), provenance=turn_text)
        elif op == "DELETE":                      # 矛盾 → invalidate，不 erase
            store.invalidate(target.id, superseded_by=fact, at=now())
            store.add(fact, vec, provenance=turn_text)
        else:                store.add(fact, vec, provenance=turn_text)   # ADD
```

salience gate 是大部分调参发生的地方。

### 5.3 检索是一个配置文件

```yaml
retrieval:
  candidate_k: 20          # 便宜的向量召回（多取）
  final_k: 5               # 真正进 context 的
  weights:
    relevance: 1.0         # cosine 基线
    recency: 0.7           # 话多的助手调高
    importance: 0.9        # 写入时 LLM 打分并存储
  recency_half_life_hours: 72
  rerank: cross_encoder
  exclude_superseded: true # 尊重写入时的失效
  query_rewrite: true      # embedding 前先解析指代
```

- 论文里三个权重都是 1，你的系统里几乎从不相等；用户名字不该衰减
- 三个标准修复：**多取再重排**（dense 检索 = 好过滤器、差排序器）；**改写查询**（"那个还行吗？" embedding 后什么都检索不到）；**尊重 supersession**（否则只是把矛盾搬进了窗口）
- Letta 的哲学：agent 是主动参与者，用工具调用**自己组织 memory 查询**

### 5.4 带保护关卡的 Compaction

- 触发在预算的 **~70–80%**（给摘要本身和接下来几轮留余量；99% 时压缩 = 恐慌压缩）
- **128k 窗口参考分配**：8k pinned system+tools · 4k core blocks · 6k 每轮刷新的检索 memory · **90k 活对话（压缩目标）** · 20k 余量
- 新纪律：**compaction 是 memory 的变更，每次变更都要回归关卡**。维护一组 **must-still-answer probes**（答案在即将压缩的片段里），压缩后断言 agent 仍能答出

```python
def compact_if_needed(ctx, store, budget, threshold=0.70, must_answer=None):
    if ctx.token_count() < threshold * budget: return ctx
    old_span = ctx.oldest_evictable_span()        # 永不碰 pinned
    summary = summarize(old_span)
    store.add(summary, provenance="compaction", at=now())   # 先写持久存储
    new_ctx = ctx.replace(old_span, summary_ref=summary)
    for probe, expected in (must_answer or []):   # PRESERVATION GATE
        assert entails(answer(new_ctx, store, probe), expected), f"compaction dropped: {probe!r}"
    return new_ctx
```

### 5.5 五步组装

**recall**（改写、多取、重排、排除已取代）→ **respond** → **remember**（后台，log 优先）→ **compact if needed**（过 probe 关卡）→ **evaluate**（行为通过率不回退才上线）。每用户一个 namespace；append-log 永不编辑。

> 不超过一页代码。全是策略。

---

## 6. Practice II · The Proof

- **Floor vs Ceiling**：recall@k / precision@k / MRR = 地板（证明管道没坏）；**天花板** = 没有那个事实就不可能做对的任务，给行动打分。两者之差 = **agent 拥有但没用的 memory**，缩小它就是整个产品
- 🧭 和 skills 的韵脚：skill 的 dexterity = 用好加载的程序，不是加载了没有；memory 也有自己的 dexterity
- **从 append-log 自建评测**（log 神圣的第三个理由：它是你的评测语料）。必须包括四个难例：**knowledge-update**、**temporal**（"迁移之前我决定了什么？"）、**abstention**（从没说过血型 → 拒答还是编？）、**distractor**

**LLM judge 是有偏的仪器**：

| 偏差 | 缓解 |
| --- | --- |
| Position bias（偏好先出现的） | 随机化顺序 |
| Verbosity bias（奖励长度） | rubric 里惩罚啰嗦 |
| Self-preference（偏好自家模型） | 遮住模型身份 |
| 总的 | **先用一小批人工标注校准** |

没验证过的 judge = 没对过米尺的尺子。

**Ship Gate**：**没有任何改动可以降低行为通过率**（新 embedding、更聪明的摘要器、重调 salience 阈值都一样）。

> 课程常设不变量：**自我改进 = 提议 + 关卡**。GEPA 在验证关卡下繁殖 prompt；skill governor 关卡每次 skill 编辑；memory governor 关卡每次写入。去掉任何一个关卡 = 把疯人院交给病人。

---

## 7. 两个 Postscript（W10 Speakeasy，都是 2026-07 的证据）

### 7.1 Markdown 赢得了规范层

所有生产系统的**规范持久层都不是向量库，是一个人类可读的文本文件夹**。

| 系统 | 做法 |
| --- | --- |
| **Claude Code** | session 开始加载 `CLAUDE.md`；学到的 notes 在**行数上限**下积累 = 穿便服的驱逐策略 |
| **OpenClaw** | **workspace 就是 agent**：`SOUL.md`（身份）、`USER.md`（人的长期上下文）、`MEMORY.md`（策展的长期事实）、按日期的 daily notes；定期 job 把 daily notes 蒸馏进 curated 文件，叫 **dreaming**（按计划的离线 consolidation） |
| **Hermes** | 磁盘上同样的形状 |

- 理由：文件可 diff、可版本、可在 harness 间迁移、对必须信任 agent 的人类可检查
- 检索是**另一个器官**：OpenClaw 默认每 agent 一个 SQLite（向量 + 全文 + BM25 混合，缺组件时退化到纯词法）
- **结构性分区**：agent A 物理上查不到 B 的 memory，因为 runtime 从不打开 B 的文件。一个 agent 一个文件 > 每次查询一个访问检查
- **Capstone 指令**：在一个 **markdown 文件夹**上教你的四个操作，不是抽象 store

🧭 这个 Obsidian vault 本身就是这种形状（我维护的规范层）。

### 7.2 Compaction 边界是设计集中的地方

三个团队在 Act II 命名的危险区（compaction 那一刻）各造了专门机制：

| 系统 | 机制 | 对应 |
| --- | --- | --- |
| **Claude Code** | **阶梯**：超大工具结果溢出到磁盘留预览 → 清旧工具结果正文 → micro-compact → 最后才整体摘要 | 免费垃圾 → 可逆 → 有损 |
| **OpenClaw** | **压缩前 memory flush**：摘要前给 agent 一个静默轮次，唯一指令是把重要的写进 memory 文件 | externalize 作为 compaction pre-hook，直接对抗 amnesia |
| **Hermes** | **辅助压缩模型**：单独的轻量 LLM 专职压缩、flush、摘要 | 后台 consolidation worker，全职雇佣 |

讨论题：你的 capstone 需要哪个？阶梯最便宜最通用；flush 保护 session 中不可替代的事实；辅助模型只在压缩量大时回本。**多数人要的是 flush。**

### 7.3 权重里的工作区（Gurnee et al. 2026, arXiv:2607.15495）

- **Jacobian lens**（修正 logit lens）：每层 ℓ 到最后一层的平均一阶因果映射 $J_\ell = \mathbb{E}_{t,t'\ge t,\text{prompt}}\left[\partial h_{\text{final},t'}/\partial h_{\ell,t}\right]$，在一千个类预训练 prompt 上平均。期望 = 分开「激活跨上下文**准备说出**什么」和「这次碰巧导致什么」
- 和 unembedding 组合 → 每个词表 token 一个残差流方向；稀疏非负组合 = **J-space**：小、特权、容量有限、可报告 / 召唤 / 保持 / 计算 / 广播
- 两个数：J-space 最多占激活方差 **10%**（通常 6–7%）；占用在约 **25** 个同时激活向量处平台化
- 发现：换掉模型默默选的运动的 J 向量 → 报告跟着变；「会结网的动物有几条腿」→ spider 在 J-space（不在 prompt 也不在输出），换成 ant → 答案 8 → 6；读 80 个无关词，只有约 **6** 个同时在场（置换，不是累积；Miller 7±2）
- **选择性**：消融 J-space → 仍能解析、流畅、分类情感，但**多跳推理崩溃**，类比 / 翻译 / 摘要掉到比未消融的小模型还差。**盲视**：西班牙语段落里拼进法语句子，J-space 的西班牙语被覆盖后仍被标记为异常
- **CoT 更鲁棒**：消融下用 CoT 解的题比直接答的明显更稳 → 把中间步骤 externalize 到纸面 = **三难在 forward pass 内部运行**；CoT = 最内层的 memory externalization
- 外面 93% 不是垃圾：解析、流畅、熟练回忆在那里跑 = 无报告的能力（Squire 的程序 / 陈述缝）

**三层嵌套工作区**：J-space（forward pass 内，几十个概念）→ context window（harness，几千 token）→ 持久存储。每层都由 write / read / consolidate / forget 治理；CoT 是第一层到第二层的管道，四个操作是第二层到第三层的管道。

**怀疑者清单**（要能和结论一起背）：一阶、语料平均的线性化（上下文依赖被平均掉）；词汇是 tokenizer 的（没有单 token 名的概念会糊或看不到）；读出是概念袋，没有绑定结构；6–10% 可能是工作区的上限，也可能只是这个钥匙孔能看到的。意识方面只声称 **access**（功能性、指标级），明确**不是现象体验**。

---

## 8. 阅读清单

**必读**

- [ ] Park et al., *Generative Agents* — 读 §4：stream、score、reflection（[已有精读](../../Generative%20Agents%20论文精读笔记.md)，用本周眼光重读 §4）
- [ ] Packer et al., *MemGPT*（arXiv:2310.08560）— context = RAM，store = disk，模型 = 自己的内核
- [ ] Liu et al., *Memory in the Age of AI Agents: A Survey*（arXiv:2512.13564）— 读解剖，注意它多安静地低估了策略问题
- [ ] Rasmussen et al., *Zep*（arXiv:2501.13956）— 双时态边、invalidation over deletion
- [ ] Liu et al., *Lost in the Middle*（TACL 2024）— 百万 token 窗口为什么不取消 memory

**选读（Oliver Twist）**

- [ ] Sumers et al., *CoALA*（arXiv:2309.02427）
- [ ] Chhikara et al., *Mem0*（arXiv:2504.19413）
- [ ] Zhang et al., *ACE*（arXiv:2510.04618）— W7 读过，用本周眼光重读
- [ ] McClelland et al., *Complementary Learning Systems*（1995）
- [ ] Ebbinghaus, *Über das Gedächtnis*（1885）— Smallville 衰减就是这条曲线戴上 γ

**夏天以来新的**

- [ ] Lin et al., *Sleep-time Compute*（arXiv:2504.13171）
- [ ] Ji, *Context Engineering for AI Agents: Lessons from Building Manus*（2025）
- [ ] Anthropic, *Project Vend*（2025）

**评测 / 安全**：LoCoMo（2402.17753）、LongMemEval（2410.10813）、AgentPoison（2407.12784）、MINJA（2503.03704）、H₂O（2306.14048）、Self-Preference Bias（2410.21819）、Chroma *Context Rot*、Gurnee et al. 2026（2607.15495）

---

## 9. 收束：十周拼成一张图

> **Prompt optimization taught the machine to improve an instruction. Memory teaches it to keep the improvement.**
> A model responds; a harness that remembers is what makes the responses belong to someone.

| 周 | 给了 agent 什么 |
| --- | --- |
| Prompts（W1–2） | 指令 |
| Skills（W3–4） | 能力 |
| Tools（W5–6） | 行动 |
| Prompt 优化（W7–8） | 改进自己的文字 |
| **Memory（W9–10）** | **过去** |

五个面 = 同一门学问：**context engineering**，决定模型看到什么的手艺。

下一步：harness（执行这份讲义写的每条策略的 runtime）→ agentic 架构 → **评测周**（这里发的每张欠条都要兑现：probe 集、行为关卡、judge 本身受审）。

---

## 10. 自测题（先默写再展开）

<details><summary>1. 四层分类和 agent 实现？</summary>working = context window；episodic = trace store；semantic = 事实库（读路径 RAG）；procedural = skill library</details>
<details><summary>2. 四个操作？为什么不是五个（加 storage）？</summary>write / read / consolidate / forget；存储很容易，区分「会记」和「只是存」的是这四个动词上的策略</details>
<details><summary>3. γ = 0.995/h 的半衰期？</summary>ln(1/2)/ln(0.995) ≈ 138 h ≈ 6 天</details>
<details><summary>4. 三项各自消融的病症？</summary>无 recency：不知道现在；无 importance：淹没在刷牙里；无 relevance：流畅自信离题</details>
<details><summary>5. agent heap 比 JVM 奇怪的两点？</summary>满了是连续退化不是阶跃；没有干净的可达性，活性是预测</details>
<details><summary>6. 三难各留下什么？决策顺序？</summary>compress → shadow；delegate → report；externalize → pointer。可重推导→丢；可分离未开始→delegate；不可替代→externalize；分散要点够→compact（最后手段）</details>
<details><summary>7. 驱逐分数为什么是乘法？</summary>一个低因子就否决驱逐，像一个 pinned 引用让 JVM 对象活着</details>
<details><summary>8. supersession vs contradiction？</summary>同一事实更新 → tombstone 旧值；两个独立来源同时不一致 → 保留 conflicts-with 边，读时解决</details>
<details><summary>9. ADK 四个 state 前缀？</summary>无前缀 = session；user: = 跨 session 跟用户；app: = 全局共享；temp: = 本次 invocation</details>
<details><summary>10. LongMemEval 里自制评测最常漏的两项？</summary>knowledge updates、abstention</details>
<details><summary>11. 三个 harness 在 compaction 边界各造了什么？</summary>Claude Code 阶梯；OpenClaw 压缩前 flush；Hermes 辅助压缩模型</details>
<details><summary>12. 课程常设不变量？</summary>自我改进 = 提议 + 关卡（GEPA 验证集 / skill governor / memory governor）</details>
