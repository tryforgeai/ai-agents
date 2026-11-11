# Week 08 学习笔记 · The Genie's Bazaar：prompt 优化能做什么、不能做什么

来源：[Week 8 - The Genies Bazaar student manual.pdf](Week%208%20-%20The%20Genies%20Bazaar%20student%20manual.pdf)（30 页，Asif Qamar，first draft 2026-11-08）+ kit `genies-bazaar/` 源码
速览版：[lesson-plan.zh.md](lesson-plan.zh.md) · 实验记录：[lab-log.zh.md](lab-log.zh.md)

> ⚠️ 这周**不是 Memory**。主题是 **Prompt 优化第二部分**：W7 学了 GEPA 怎么工作，W8 去测它的边界。

> **An optimizer can only change what goes into the prompt. It cannot change the weights of the model that reads the prompt.**
> 这就是 prompt 优化便宜的原因，也是它有上限的原因。今天每个任务都在演示这句话的某一半。

---

## 0. 一句话 + 四个目标

**今天的问题**：便宜模型答不好时，缺的是**信息**（可以写进 prompt）、**知识**（得靠检索或微调补事实），还是**能力**（只能训练）？花钱之前怎么判断？

下课时应该会：

1. 搭一个**公平比较**：naive prompt vs 前沿模型 vs 优化后的便宜模型，用一个到最后才打开的 **sealed test set**
2. 写一个返回**分数 + 一句反馈**的 metric，并说清楚为什么这句话对 GEPA 很重要、对 MIPROv2 几乎没用
3. 从任务的**形状**预测哪个优化器会赢
4. 面对新任务，判断差距是**缺信息**（优化能补）还是**缺能力**（补不了），以及该用什么补

---

## 1. 今天的安排（排灯节，提前结束）

| 时间 | 环节 | 讲义位置 |
| --- | --- | --- |
| 11:15 | Deep dive 收尾：GEPA、MIPROv2、记分板 | The ideas in one sitting |
| 13:00 | 百家饭午餐（可以边吃边开始做 stall） | |
| 13:45 | **两个 Stall**：Hostile Registry、House Taxonomy | The stalls |
| 15:00 | **两扇 Door**：Library、Gymnasium | The doors |
| 15:30 | Debrief：信息 vs 能力的地图 | The map |
| 16:15 | Owl of Minerva（有时间才做） | |
| 17:00 | 下课。没有客座讲座，也没有 Speakeasy | |

**核心路径**：Stall 1 → Stall 2 → Door A → 有时间再做 Door B。做不完很正常，先问邻座再问讲师。

**两位精灵**：

- **Reflecting Genie = `dspy.GEPA`**：读文字写的失败原因，重写 prompt
- **Tasting Genie = `dspy.MIPROv2`**：试很多种措辞和示例组合，记下哪个分数高

---

## 2. 地图：四个任务，四种缺口

| 位置 | 缺什么 | 任务 | 预期 |
| --- | --- | --- | --- |
| **Stall 1** Hostile Registry | **信息**：API 的真实行为（文档写错了） | agent 用 4 个工具操作一个小支付账本 | 优化器发光，偏 GEPA（规则能用一句话说清） |
| **Stall 2** House Taxonomy | **信息**：一条没人写下来的归档规则，只体现在标注里 | 把商户便签分进 12 类 | 偏 MIPROv2（规则难说出口，只能靠示例） |
| **Door A** Library | **知识**：冷门人物和地点的事实 | PopQA 长尾问答，闭卷和检索两种 | 优化帮不上，**检索**才有用 |
| **Door B** Gymnasium | **能力**：搜索算式的技能 | Countdown 凑数 | 优化有上限，**RL（GRPO）**改权重 |

**Stall 和 Door 的区别**：在 Stall，模型已经有能力，只缺一条信息，写进 prompt 或示例就行。在 Door，Door A 的事实得靠另一种工具（检索）补；Door B 不管给多少信息都没用，因为缺的是技能本身。

---

## 3. 核心概念

### 3.1 优化器能动什么，不能动什么

输出好不好取决于两样东西：**权重能做什么**，以及 **prompt 告诉了它什么**。prompt 优化只搜第二样。

- **能加的**：一条模型不知道的规则、一个格式示例、一个陷阱提醒、一个事实
- **不能加的**：权重做不到的事；以及一个**既不在权重里、也没有给优化器看过**的事实

两种诊断从外面看一模一样，都是答错，所以今天整天都在练怎么区分。

### 3.2 DSPy 四个概念（读懂 kit 里每个文件就够了）

| 概念 | 是什么 | kit 里的例子 |
| --- | --- | --- |
| **Signature** | 输入 → 输出，docstring 就是模型看到的指令 | `NoteSig`（note → category） |
| **Module** | 包一层策略：`Predict` 直接答、`ChainOfThought` 先推理、`ReAct` 循环调用工具（= agent） | Registry 用 `ReAct`，Library RAG 用 `ChainOfThought` |
| **Metric** | 拿预测和 gold 比，给分数 | 每个 stall 的 `scorer` |
| **Optimizer** | 输入 module + metric + 示例，`compile` 之后返回改进过的 module | `dspy.GEPA` / `dspy.MIPROv2` |

每个 stall 结构相同：**signature + program + scorer（分数 + 原因）+ 跑 arms 的命令**。读懂一个，其余都能读懂。

### 3.3 GEPA：糖果店的货架（Pareto pool，W7 复习，表述更严谨）

- 货架上每份「配方」是一个完整的候选 prompt
- 货架不只留平均分最高的，而是留**在至少一个训练样本上最好**的所有配方。平均很普通、但在第 17 题上无人能敌的配方也会留下，因为下一代可能正需要它那一部分
- **支配**：用 $s_A(i)$ 表示候选 A 在第 i 题的分数。若对所有 i 都有 $s_A(i) \ge s_B(i)$，且至少有一题严格大于，就说 A 支配 B。被支配的候选在你测过的每一方面都不更好，删掉不损失任何东西
- **每一轮四步**：
  1. 从货架抽一个候选（在更多题上最好的候选权重更高）
  2. 在几道训练题上跑，**用文字读出哪里错了**
  3. 让 reflector（强模型）据此重写
  4. 给重写打分；够格就上架，同时移除它新支配的候选
- 有时还会 **merge**：把一个候选擅长的指令和另一个候选擅长的指令拼起来，专才的贡献就这样传给后代
- **Intron（内含子）**：不改变行为的那部分文字。加了内含子的改写等于没进步，这也是 sealed test 存在的理由之一：读起来漂亮但什么都没改变的指令，在 test 上拿不到分

### 3.4 MIPROv2：一段话版

- 同时搜**指令**和**示例（demos）**两样东西
- 提出几条指令，再从训练数据和模型自己答对的尝试里凑出几组示例
- 用 **TPE（tree-structured Parzen estimator，一种贝叶斯方法）** 决定下一个试哪种组合，把预算集中花在已经表现好的区域附近
- 结果是一条指令加几个**作为一组选出来**的示例

### 3.5 两位精灵对比（后两行是猜测，今天去验证）

| | GEPA（Reflecting） | MIPROv2（Tasting） |
| --- | --- | --- |
| **读什么** | 分数 + 一句「哪里错了」 | 分数 + 可选的示例 |
| **改什么** | 重写指令 | 搜索指令和示例的组合 |
| **保留什么** | 每个在某方面最好的候选 | 找到的最佳组合 |
| **猜：什么时候最强** | 修法能写成一条规则 | 规则只体现在示例里 |
| **猜：风险** | 反馈指错方向 | 对噪声标签过拟合 |

### 3.6 改词还是改权重：RL vs GEPA

| | GRPO（RL，可验证奖励） | GEPA |
| --- | --- | --- |
| 改什么 | **权重** | **文字** |
| 每次尝试看到什么 | 每个 completion **一个数** | 分数 + **为什么不对** |
| 优点 | 改进带到所有地方，没有 prompt 开销 | 一句反馈的信息量比一个标量多，所以**需要的尝试少得多**（GEPA 论文的主张） |
| 局限 | 要几个小时的硬件，还要可验证奖励 | 学到的东西必须塞得进 prompt，**而且是原模型用得上的** |

GRPO 的做法：每个 prompt 采样多个 completion，打分，把权重推向比同组兄弟分数更高的那些。Door B 让两者在同一个模型、同一个任务、同一个 metric 上正面比较。

### 3.7 ⭐ 会自我解释的 metric（今天唯一要写或改的代码，讲义说「慢慢读」）

```python
def scorer(gold, pred):
    if pred.category == gold.category:
        return 1.0, "Correct."
    return 0.0, (f"The house files this note under {gold.category}; "
                 f"the answer was {pred.category!r}.")
```

- MIPROv2 **只用分数**，忽略那句话；GEPA **两样都读**
- 写法：**就像对犯错的同事说话**，说清哪里错了、本该怎样，用任务本身的语言。不要说「分数低」
- 只说 "wrong" 等于什么都没给 reflector；说清错误从哪来，就给了它一条可以写下来的规则
- kit 里的实现（`arms.py: make_metrics`）：一个 scorer 生成两个 metric。`gepa_metric` 返回 `ScoreWithFeedback(score, feedback)`，`plain_metric` 只返回 float

### 3.8 记分板：五个 arm，三条规则，一个噪声公式

**五个 arm**（每个任务都报同样的五项，方便跨任务比较）：

1. **Naive**：便宜模型 + 种子 prompt
2. **Frontier, naive**：强模型 + 同一个种子 prompt
3. **Frontier + demos**：强模型 + 所有标注示例放进上下文（有标注的任务才有这一项）
4. **Cheap + GEPA**
5. **Cheap + MIPROv2**

**三条诚实规则**：

1. **train / dev / sealed test** 三分：优化器从 train 学，用 dev 选候选；test 到最后才看。**偷看 test 来二选一，test 分数就作废**
2. 随机性的 arm 跑**多个 seed**，单次可能只是运气好
3. 每个 arm 的 **metric 调用预算相同**，赢不能只靠多花钱

**噪声**：n 道题上得分 p，标准误约为

$$\mathrm{SE} \approx \sqrt{p(1-p)/n}$$

讲义的例子：p = 0.2、n = 200 → SE ≈ 0.03。**两个分数相差不到 2 个 SE 就分不出高低**，这时诚实的说法是「这个 test set 上分不出来」。

> 🔎 **我的补算**：Registry 的 sealed test 只有 **30 题**（见 §4.1），p = 0.5 时 SE ≈ **0.09**，两个 arm 要差约 **0.18** 才算真的有差别。Library 每个 band 只有 26 道 test 题，看按 band 拆开的分数时尤其要小心。

**全天带着的三个问题**：

1. 每次运行：优化器往 prompt 里加了什么模型原本没有的东西？
2. 每次赢：强模型配同样的 prompt 也会赢吗？
3. 每次输：要找的信息本来存在吗？

---

## 4. 两个 Stall（模型有能力，只缺一条信息）

### 4.1 Stall 1 · The Hostile Registry（文档会说谎的 API）

**场景**：集市的支付账本，24 个客户、几百个订单，4 个工具：`find_customer`、`list_orders`、`get_order`、`refund`。agent 收到自然语言问题，调用工具直到给出答案或完成修改。**工具描述是赶工写的，跟 API 的真实行为不一致。**

**任务**：60 题，6 类各 10 题：`total_since`（某日之后总额）、`count_since`（订单数）、`latest`（最新订单）、`oldest`（最早订单）、`refund_partial`（部分退款）、`refund_latest_remainder`（把剩余部分全退）。程序生成，程序验证；0/1 计分。**验证器也检查账本最终状态**：退错订单，就算 agent 说 done 也是 0 分。

**切分**（`registry.py: split`）：每类 3 / 2 / 5 → **train 18 · dev 12 · test 30**。

**做什么**：先读 `stalls/ledger.py` 里 4 个工具的描述 → 写预测 → 跑 naive，读至少 3 条 trace → 同预算跑 GEPA、MIPRO → **先读两者写出的指令，再看分数**（讲义说这是全天最好读的输出）→ 跑强模型 + naive prompt 对比。

```bash
uv run python -m bazaar.stalls.registry --arms none --seeds 1                    # smoke
uv run python -m bazaar.stalls.registry --arms none,gepa,mipro --seeds 3 --budget 150 --out runs/registry
uv run python -m bazaar.stalls.registry --arms none --role frontier --out runs/registry-frontier
uv run python -m bazaar.stalls.registry --arms gepa --feedback minimal ...        # Try this 1：只说 Correct/Wrong
```

<details><summary>🔒 源码里的「文档 vs 真实行为」对照（先自己读 trace 找，再展开）</summary>

| 工具 | 文档说 | 真实行为 | 出错时有没有报错 |
| --- | --- | --- | --- |
| `find_customer` | 大小写不敏感，"First Last" 或 "Last, First" 都行 | **只认 "Last, First"，精确匹配且区分大小写** | 🔊 有：`no customer matches that name` |
| `list_orders` 的 `since` | ISO `YYYY-MM-DD` | **`DD-MM-YYYY`** | 🔊 有：`since must be DD-MM-YYYY` |
| `list_orders` 的 `page` | 从 1 开始（函数默认值也是 `page=1`） | **从 0 开始** | 🔇 **静默**：直接跳过最新的 5 单 |
| `list_orders` / `get_order` 的 `amount` | 卢比 | **paise（1/100 卢比）** | 🔇 **静默**：总额大 100 倍 |
| `refund` 的 `idempotency_key` | 可选 | **≥ 500 卢比必填** | 🔊 有 |
| `refund` 超额报错的 `remaining` | （没写） | **单位是 paise**，而 `amount` 参数是卢比 | 🔊 有，但单位不一样 |

**规律**：会报错的不一致，agent 多半自己能纠正；**静默的（页码、单位）它永远发现不了**，这就是 Questions 1 想让你发现的那组共同点。

我注意到的一个细节：`tasks.py: verify` 里「页码从 0 开始」那条反馈**故意跳过了 `latest` 类**（`task.kind != "latest"`），可 agent 用默认 `page=1` 时拿到的「最新」订单其实是第 6 新的。也就是说 `latest` 题错了只会收到「Final answer wrong」，没有页码提示。这一类上 GEPA 会不会更难学到页码规则，值得看。

</details>

**先写预测**：naive 便宜 agent 的 test 分数；强模型配同一个 prompt 会好很多吗、为什么；哪个精灵更强、强多少；赢家的指令里会出现哪句话。

**读 trace 的方法**：每个失败任务，找出**第一个本可以学到东西却没学到的调用**。当时 agent 相信什么？要看到什么它才会改变看法？带报错的失败和返回干净结果的失败是两回事。

**Questions（答案都在自己的运行结果里）**：

1. 哪些不一致 agent 能自己恢复，哪些从来没发现？两组各有什么共同点？
2. 强模型读同样的文档，会掉进同样的坑吗？这说明原因是推理弱，还是文档本身不可信？
3. 赢家的指令里，哪些句子是**关于这个 API 的事实**，哪些是**通用建议**？哪种更有用？
4. 找一题答案对但得 0 分的（账本状态错了）
5. 最佳候选出现前优化器花了多少次 metric 调用？预算需要多大？
6. 这里的 scorer 知道 API 的真实行为，**真实系统很少有这么全知的 scorer**。你会用什么代替？结果能保留多少？

**Try this**：① 反馈改成只说 "wrong"（`--feedback minimal`），重跑 GEPA；② 预算减半，看收益在哪里停止；③ 在 `ledger.py` 加第 6 个不一致，再加一题去触发它。
**Stretch**：故意让反馈指错原因（比如把页码错误归咎于日期格式），看精灵跟着这句话走还是跟着证据走；再写一个只看最终答案的反馈函数做对比。

> **The lesson**：只要 metric 里有东西告诉优化器发生了什么，它就能把**关于系统的知识**从它所在的地方（API 的行为）搬进 prompt。文档（哪怕是错的文档）也是一种 prompt，模型分不出哪句是假的。**修复它的是证据，而证据通过反馈句到达优化器。** 更强的模型并不能免掉对证据的需要。这里 scorer 知道 API 的真实行为并直说，是 GEPA 的**最佳情况**，Stretch 就是在测反馈变差后收益还剩多少。

### 4.2 Stall 2 · The House Taxonomy（说不出口的归档规则）

**场景**：集市办公室把商户便签归入 12 个类别，例如「Stock check on laddus along with filter coffee before Diwali.」办公室有一条归档规则，**没人写下来过**。共 300 条已归档便签：**train 60 · dev 40 · test 200（sealed）**。train 和 dev 里有百分之几的标签是错的，因为店员累了或者赶时间。

**难点**：英语模型当然读得懂，但它不知道 house rule：便签提到两类货时哪一类胜出；某件货两类都说得通时归哪一类。规则是一致的，能从示例里恢复出来，但**很难用一句平实的话说清**。

**做什么**：自己先读 30 条便签，**写下你猜的规则** → 写预测 → 跑 naive，再把所有标注塞给强模型 → 同预算跑两位精灵 → 比准确率、成本、seed 间的波动。

```bash
uv run python -m bazaar.stalls.taxonomy --arms none                    # smoke
uv run python -m bazaar.stalls.taxonomy --arms none,fewshot,frontier-fewshot,gepa,mipro --seeds 3
```

> ⚠️ 规则写在 `stalls/taxonomy.py` 里。**写下自己的猜测之前别打开**，也别剧透给还没试的邻座。最后拿自己的猜测和文件比对，是这一站最好玩的部分。

<details><summary>🔒 我从源码里数出的数据形状（不含规则本身）</summary>

- 35% 的便签提到**两类**货（优先级规则在这些便签上才起作用）：train 20/60、dev 11/40、test 64/200
- 噪声标签：train **3** 条、dev **3** 条、test **0** 条（test 是干净的）
- `fewshot` / `frontier-fewshot` 是把 train + dev **全部 100 条**都塞进 demos，其中含 6 条错标签
- MIPRO 默认 `max_demos=4`（Try this 2 改成 10，在 `arms.py` 的 `run_mipro`）

</details>

<details><summary>🔒🔒 规则答案（写完自己的猜测后才展开）</summary>

1. **优先级**：两类同时出现时，取这个顺序里靠前的：Perishable > Gifting > Winter > Sweets > Beverages > Garments > Spices > Jewellery > Footwear > Lighting > Decor > Toys
2. **反直觉的归属**：lassi 归 **Perishable**（不是 Beverages）；pashmina shawls 归 **Winter**（不是 Garments）；fresh marigold garlands / fresh rose petals 归 **Perishable**；gift hamper 压过里面装的东西，**除非里面有易腐品**

→ 第 1 条其实能用一句话写出来（一张优先级表），第 2 条是一堆零碎例外。所以可以看看 GEPA 会不会把优先级表写进指令，而 MIPRO 靠示例。

</details>

**先写预测**：你自己写的规则；naive 准确率；把所有标注给强模型能不能补上差距、标注里的错有没有影响；哪个精灵赢、赢家的程序带着什么是另一个没有的。

**看什么**：看错误的**模式**，不只看总分。能用一句话说清的规则会在错误里留下规律，噪声不会。看哪个精灵的指令里写了规则、哪个只带示例、哪个两样都有。看 MIPRO 留下的示例是典型的，还是模型答错的那种怪例。

**Questions**：

1. 你自己写的规则在 sealed 便签上表现如何？在哪里失败？
2. 强模型拿到所有标注时，是**学到了规则**还是**照抄最近的例子**？从它的错误怎么分辨？
3. 在 train 里找一条错标签。两个优化器各怎么处理它？
4. 按 **1 万条**便签算成本（不是 200 条），你会部署哪个？为什么？
5. 有精灵把规则明确写下来了吗？对明年接手维护系统的人，哪种结果更有用？

**Try this**：① 把 `make_notes` 的噪声从 5% 调到 20%，看哪个精灵退化更快；② MIPRO 示例从 4 个加到 10 个；③ 改 scorer，让「相邻类别」的错扣分少于「远类别」的错。
**Stretch**：用自己工作里的分类任务做一个 stall。规则能用一句话说清就预测 GEPA 赢，说不清就预测 MIPRO 赢，然后验证。

> **The lesson**：指令只能装**有人能说出口**的规则。规则琐碎到说不出、却体现在示例里时，**示例能装下文字装不下的东西**，而把示例**作为一组来挑**的优化器有优势。拿着所有示例的强模型是个很强的对手，这时优化的理由是**成本和一致性**：便宜模型 + 短 prompt + 几个精选示例，跑一万次。**标签噪声是优化器的风险，它会忠实地学会店员的错误。**

---

## 5. 两扇 Door（优化器多半不是赢家）

### 5.1 Door A · The Library（缺的是知识）

**场景**：关于冷门人物和地点的问题，例如「In what city was Emily Hood Westacott born?」。来自 **PopQA**（Mallen et al. 2212.10511），每题带主题词条在 Wikipedia 上的阅读量，用来近似知名度。按知名度切成 **5 个 band**（rarest → famous），每个 band 40 题。

- **闭卷**：靠权重记忆。名人见过很多次，冷门的可能只见过一次或从没见过。**prompt 里写什么都补不出一个没人提供过的事实**
- **开卷**：给模型一个「图书馆」，就是 903 段 Wikipedia 词条开头 + 一个简易 **BM25** 关键词检索（`run.py` 里约 30 行，值得通读），指令是「根据给你的页面回答，否则说不知道」
- **Metric**：答对 **1**，诚实说「I do not know」**0.25**，答错 **0**。反馈还会告诉优化器**答案在不在检索到的页面里**，这样检索失败和阅读失败就能区分开

**4 个 arm**：`small-closed`、`frontier-closed`、`small-rag`、`small-rag-gepa`

```bash
uv run python -m bazaar.door_a.run --arms small-closed --limit 20 --out runs/door_a-smoke   # smoke
uv run python -m bazaar.door_a.run --seed 0 --out runs/door_a
```

**先检查图书馆的天花板**（`data/door_a/build_stats.json`，每个 band 里「答案出现在应检索词条开头」的比例）：

| band | rarest | rare | middle | known | famous |
| --- | --- | --- | --- | --- | --- |
| answer_in_lead | 0.875 | 0.95 | 0.95 | 0.95 | **0.85** |

→ 这是任何读者能达到的**最高分**，不是 100%。有意思的是 **famous 反而最低**（我的推测：名人词条开头篇幅留给成就，未必写出生地之类的细节；待核实）。检索没带回来的答案，模型找不到；**优化器也不能靠改 prompt 修好检索**。

> 🔎 **一处和讲义不一致**：讲义说 sealed test「约 160 题」，但 `run.py` 每个 band 切 **8 train / 6 dev / 26 test** → test 只有 **130 题**。另外 `data/door_a/_stale_do_not_use/` 是旧版数据，别误用。

**先写预测**：便宜模型闭卷分数随 5 个 band 的曲线（直线、曲线还是悬崖）；强模型闭卷线在哪；便宜模型 + 图书馆 vs 强模型闭卷；GEPA 在图书馆之上还能加多少。

**Questions**：

1. 闭卷准确率随知名度是平稳上升还是台阶式？更大的模型会把曲线怎么变？
2. 比较每个 arm **每答对一题的成本**，哪个最划算、在什么问题量下？
3. RAG arm 答错的题里，多少是**页面没检索到**，多少是**检索到了但读错**？
4. 优化器改了 prompt 的什么？为什么好的检索给它留的改进空间很小？
5. 把 `ABSTAIN_CREDIT` 从 0.25 改成 0 再改成 0.5，闭卷 arm 的行为怎么变？

**Try this**：检索页数从 3 改成 1 和 6，看检索在哪里不再有帮助、成本怎么变；让模型说出依据的是哪一页并给它打分；把 BM25 换成 RAG 课里学的检索器。
**Stretch**：写 5 道需要**两页两个事实**的题（例如某公司创始人的出生地）。第一次检索不知道下一步该查什么，流水线哪里先坏？优化器能修吗？

> **The lesson**：**一个模型没有的事实，优化不进去。** prompt 能做的，是告诉模型去哪里找，以及找不到时该怎么做。小模型 + 图书馆可以胜过大得多的闭卷模型。**改变可用信息的工具（检索）和优化器是两回事**，永远先判断缺口是不是知识缺口。检索已经接近天花板时，优化器就没什么可找的了。

### 5.2 Door B · The Gymnasium（缺的是能力）

**场景**：Countdown 凑数。给几个数和一个目标，用 + − × ÷ 写出等于目标的算式。来自英国电视智力节目。有两个好性质：**程序能精确判对错**（不需要评委）；小模型做得差的原因**和知识无关**，因为它得在算式空间里**搜索**，不断尝试、丢弃。

- 模型：**Qwen2.5-3B-Instruct**（讲师 GPU 服务器上用 vLLM 提供服务），所有方法都在同一套权重上试
- 数据：**4000 train / 60 dev / 200 sealed test**，每题 4 个数（1–60），目标 10–999
- 优化器的 scorer：对 1、错 0；反馈说明为什么错（数字用了两次、值不等于目标、解析不了）
- **RL 的 reward 多一项**：格式正确但答错给 **0.1**，让训练有个起点可以往上爬

**三种改进方式**：① 不动权重、改 prompt（GEPA / MIPRO）② **RL（GRPO，TRL 的 `GRPOTrainer`）** 改权重 ③ naive 基线。
**今天不自己训练**，讲师课前已经开跑（两块大 GPU 也要几个小时）。我们读它的**训练日志和各 checkpoint 分数**。

```bash
uv run python -m bazaar.door_b.po --base-url http://<server>:8001/v1 \
    --student-model Qwen/Qwen2.5-3B-Instruct --arms none,gepa,mipro --seeds 3
uv run python -m bazaar.door_b.po --student-model qwen/qwen-2.5-7b-instruct --arms none,gepa --seeds 1   # 服务器忙时的托管备选（更大的模型！）
uv run python -m bazaar.door_b.evaluate --base-url http://<server>:8001/v1 --model Qwen/Qwen2.5-3B-Instruct --label base
```

**RL 配置速记**（`rl_grpo.py` / `scripts_rl_server.sh`）：400 步、每个 prompt 8 个 generation、lr 1e-6、**max_completion 512 token**、`beta=0`（不加 KL 约束）、temperature 1.0、每 50 步存一个 checkpoint；vLLM colocate 生成。

**做什么**：先**手解 3 道题并计时**，注意自己在做什么（尝试 → 丢弃）→ 写预测 → 跑 naive 和两位精灵 → 读 RL 日志和 checkpoint 分数 → 在一页纸上画两张图：**分数 vs 成本**、**分数 vs 投入**。

**⭐ 看什么：把两种改进分开**

- **格式失败**（没按要求输出）是指令问题，prompt 能修
- **算式算不到目标**是能力问题
- evaluator 两个都报：**well-formed 比例**和**正确比例**。每种方法都看清是哪个在动
- **还要看答案长度**：RL 把 completion 截在固定 token 数（512），被「格式正确」奖励的模型可能学会在答案前**少写**。如果是这样，一部分增益来自**简短**而不是技能。看到任何数字，都问一句：**跟它一起变的还有什么？**

**先写预测**：naive 准确率；两位精灵各能把它带到多高、更好的那个 prompt 会写什么；RL 能到多高，分数随训练怎么变（平稳、跳跃、还是平的）；训练过程中答案会变长还是变短、为什么这会影响结论。

**Questions**：

1. 每种方法里，哪些改进来自格式、哪些来自能力？
2. 更好的那个精灵写的指令，一个人照着做能解出 naive 模型解不出的题吗？它能教什么、不能教什么？
3. RL 学习曲线上，大部分增益出现在哪？之后发生什么？
4. 要判断平台期是**方法**的性质还是**设置**的性质，你会改训练里的什么？
5. 你是付钱的人：每天 1 万道这种题，从哪种方法开始？什么结果会让你换？

**Try this**：① 改 `po.py` 的种子 prompt，加一句搜索策略（「先试最大的数」），看手工能复现多少精灵找到的东西；② 让反馈说更多（列出没用到的数）或更少（只说 wrong）；③ 放宽答案长度上限再评估一次。
**Stretch**：换一个更大的模型跑同样的 prompt 优化 arm。如果 naive 和优化后的差距**缩小**，说明技能是**用得不够**而不是**缺失**。再预测：给 3B 的 RL 更多推理预算，平台期会在哪里？怎么验证？

> 🔎 **源码里注意到的三处**：
> 1. 讲义说每个数「**最多**用一次」，种子 prompt 和 `countdown.check` 实际要求「**恰好**用一次」（`Counter(used) != Counter(numbers)` 就判错）
> 2. RL 用的 `PROMPT_TEMPLATE` 要求 `<think>` / `<answer>` 标签；PO arm 用的是 DSPy 的 `ChainOfThought`，输出字段是 `answer`，scorer 找不到标签时退回取 `=` 左边。**两条路的「格式」定义不一样**，比较 well-formed 比例时要记住
> 3. 托管备选是 **7B**，不是 3B。用它跑出来的数字不能直接和 3B 的 RL 比

> **The lesson**：有些失败是**能力**问题。prompt 能告诉模型答案长什么样、该试哪种搜索，对小模型有点用，但**加不出搜索能力**。训练可以，因为它改权重，代价是几个小时的硬件和一个需要**可验证奖励**的流程。两种方法都有会限制上限的设置，**结果只和背后的实验一样可靠**。看到增益时，要问还有什么跟着变了。

---

## 6. ⭐ Debrief：信息还是能力？（今天最该带走的）

### 6.1 两个问题，四个格子

花钱之前问两个问题：**更大的模型能解吗？优化器能替便宜模型补上差距吗？**

| | **优化器能补上** | **优化器补不上** |
| --- | --- | --- |
| **大模型能解** | 缺的是便宜模型**用得上的信息**。→ **优化，省下钱** | 缺的是便宜模型**没有的知识或能力**。→ 花钱上大模型，或**换工具** |
| **大模型也不能解** | 任务**没说清楚**，优化器的示例或反馈补上了缺的规格 | 任务超出两者能力，或**定义不清**。→ **重新想任务** |

**三条今天之后也适用的建议**：

- **缺信息** → 放到模型看得见的地方：prompt、示例，或检索步骤
- **缺知识** → 检索，或在这些事实上微调
- **缺能力** → 训练
- 不管哪种，**先说清是哪种缺口，再买药**

### 6.2 新任务的五步诊断

1. **拿到同样文档的人能做吗？** 能干的人给对指令就能做 → 多半是**信息**缺口
2. **更强的模型用同一个 prompt 能做吗？** 能 → 权重做得到，再问便宜模型的 prompt 能不能装下强模型有的东西
3. **答案是事实还是技能？** 事实需要**来源**；技能需要**练习**，也就是训练
4. **你的 metric 告诉优化器原因了吗？** 没有 → 别指望 GEPA 比瞎猜好多少，考虑 MIPROv2 + 示例
5. **证据是 sealed 的吗？** 看过 test set，结果就不算数

### 6.3 我的预填（课前推断，下课后用自己的运行结果改）

| 任务 | 我的预测 | Naive | 最佳 arm 和分数 | 缺口类型 |
| --- | --- | --- | --- | --- |
| Registry | GEPA > MIPRO；frontier-naive 也会掉进静默的坑 | | | 信息（API 行为） |
| Taxonomy | MIPRO ≥ GEPA；frontier-fewshot 很强但贵 | | | 信息（隐藏规则） |
| Library | small-rag ≫ frontier-closed（冷门 band）；GEPA 增量小 | | | 知识 |
| Gymnasium | PO 主要动 well-formed，正确率涨得少；RL 早期跳一下然后平台 | | | 能力 |

---

## 7. 下课前要回答的问题

1. 哪个预测离实际最远？我当时假设了什么？
2. 今天哪个任务的结果最可信、哪个最不可信？用 test set 大小、seed、噪声来说明
3. 选一个自己工作里的任务：它在地图哪一格？最便宜的验证实验是什么？
4. 模型换成新版本时，优化带来的收益会在哪里消失？今天哪些收益会留下来？
5. 要阻止优化器学到你不想要的东西，metric 需要怎么改？

> 💡 **和 Capstone（Verifiable Commerce Agents）的联系**：Stall 1 基本就是 Capstone 的缩小版，一个 agent 操作带副作用的 API，用验证器检查最终状态。可以借鉴三点：① 验证器同时查**答案**和**状态**；② 把**静默**的不一致（单位、分页）和**会报错**的分开看；③ Q6 那种「真实系统没有全知 scorer」是 Capstone 必须面对的问题。

---

## 8. 术语表

| 术语 | 含义 |
| --- | --- |
| **Abstention** | 回答「不知道」；Library 给部分分（0.25） |
| **Arm** | 记分板上的一种方案：naive、强模型、GEPA…… |
| **BM25** | 按查询词匹配程度给文档排序的关键词方法 |
| **Budget** | 优化器允许花的 metric 调用次数 |
| **Dominance** | A 在每题上不差于 B，且至少一题更好 |
| **Feedback** | scorer 随分数返回的那句话 |
| **GEPA** | 读文字反馈、重写 prompt、保留 Pareto 池的优化器 |
| **GRPO** | 比较同一 prompt 的多个 completion，把权重推向更好那些的 RL 方法 |
| **Intron** | 不改变行为的候选片段 |
| **MIPROv2** | 用贝叶斯方法（TPE）联合搜指令和示例的优化器 |
| **Pareto pool** | 没有被任何候选支配的候选集合 |
| **ReAct** | 推理 → 调工具 → 读结果 → 重复 |
| **Sealed test set** | 最终打分前任何优化器、任何人都没看过的样本 |
| **Seed** | 随机数种子，换种子得到随机方法的另一次运行 |
| **Verifiable reward** | 程序能精确算出的分数，例如算式是否等于目标 |

---

## 9. Kit 地图与上手

```
genies-bazaar/
├── src/bazaar/
│   ├── llm.py          # 模型角色：student=claude-haiku-5.5；reflector/frontier/judge=claude-opus-5.5；OpenRouter + ZDR
│   ├── arms.py         # 记分板机器：run_none / run_gepa / run_mipro / record / summarize
│   ├── stalls/         # ledger.py + tasks.py + registry.py（Stall 1）；taxonomy.py（Stall 2，规则在里面！）
│   ├── door_a/         # data.py（建库，今天不跑）；run.py（BM25 + 4 arms）
│   └── door_b/         # countdown.py（验证器 = reward）；po.py；evaluate.py；rl_grpo.py（TRL，没在作者环境跑过）
├── data/               # door_a：questions 200 / corpus 903；door_b：4000/60/200
└── tests/              # 23 个，不需要网络和 key
```

**GEPA 参数**（`arms.py`）：`reflection_minibatch_size=3`、`candidate_selection_strategy="pareto"`、`max_metric_calls=budget`；**MIPRO**：`auto="light"`、`max_bootstrapped_demos = max_labeled_demos = 4`。

**上手顺序**：

```bash
uv sync
cp .env.example .env        # 贴 OpenRouter key，不加引号；投屏时别露 key
uv run pytest -q            # 23 passed，不联网
uv run python -c "from bazaar.llm import *; load_env('.env'); import dspy; dspy.configure(lm=make_lm('student')); print(dspy.Predict('q -> a')(q='Say hello.').a)"
```

**两个手册没提的小工具**：

```bash
uv run bazaar doctor                 # 一次检查 key、student 和 reflector 能不能调通、DSPy 有没有 GEPA/MIPROv2
uv run python -m bazaar.report runs  # 把 runs/ 下所有结果汇成一张 markdown 记分板（自动跳过 smoke）
```

⚠️ `report.py` 注释说：11/7 最早录的 run，cost 列记的是**累计**花费，后几个 seed 的成本偏高；之后的 run 已修好。

**两个习惯**：每条命令先用 smoke 参数跑（打错字只损失 10 秒，不是 10 分钟）；**保留每次运行的输出目录**（`runs/`），对比全靠它。**先调低预算，再调高。**

**常见问题**：key 报错 → `.env` 在 kit 根目录、key 不加引号；"No endpoints found matching your data policy" → 那个模型没有 ZDR endpoint，用 `llm.py` 的默认值；truncated 警告 → smoke 时无害，正式跑就调大 `max_tokens`；optuna 报错 → 重跑 `uv sync`；太慢 → 降 budget、加 threads；两次分数不同 → 正常，见噪声公式；找不到模块 → 在 kit 根目录用 `uv run`。

---

## 10. 延伸阅读

| 论文 | arXiv | 对应 |
| --- | --- | --- |
| Agrawal et al., **GEPA**: Reflective Prompt Evolution Can Outperform RL | 2507.19457 | Reflecting Genie，和 GRPO 的比较 |
| Opsahl-Ong et al., Optimizing Instructions and Demonstrations for Multi-Stage LM Programs（**MIPRO**） | 2406.11695 | Tasting Genie |
| Khattab et al., **DSPy** | 2310.03714 | 框架 |
| Mallen et al., When Not to Trust Language Models（**PopQA**） | 2212.10511 | Library 的问题来源、长尾 |

外加 DSPy 文档；W7 Reservoir §1（MIPRO 谱系、TPE）、§2（优化器大全）、§4（成本估算）。
