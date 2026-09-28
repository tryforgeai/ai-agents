# AI Agents Week 02 — The Literal Genie of the Strange Lamp（2026-09-27）

课程：**AI Agents Bootcamp** · SupportVectors AI Lab · Fall Cohort
主题：*The Literal Genie of the Strange Lamp — **Prompting by Hand***
时间：**11:00 – 19:30**（含 13:20 午饭、16:15 休息）
讲义：[`uploads/fall-agents-week-2-lesson-plan.pdf`](uploads/fall-agents-week-2-lesson-plan.pdf)（21 页，作者 Asif Qamar，first draft 2026-09-27）

> **本周题眼**
> *Whatever you leave unsaid, the model fills with the mode of the internet.*
> 精灵不邪恶，只是**字面主义**（literal）。它严格执行你说出口的话，其余全用先验填补。

> **⚠️ 与 Week 00/01 不同：本周有独立的 lesson plan PDF，不是复用 deck。**
> 全天判断标准是"**凭感觉**"——没有分数、没有排行榜。讲义明说这是刻意设计的痛苦，
> 目的是让下周的自动优化器（DSPy / GEPA）显得**必需**而非强加。

## 目录

| 文件 | 内容 |
| --- | --- |
| ⭐⭐⭐ [`复习总纲.zh.md`](复习总纲.zh.md) | **复习就看这一份**：一条主线 · 十个核心概念 · 写法 12 条 · 安全 · 数字速查 · 28 道自测题 · 复习路线 |
| ⭐⭐ [`lesson-plan.zh.md`](lesson-plan.zh.md) | **听课速览**：全天主线 / 七幕重点 / 时间表 / 作业 / 必读 |
| ⭐⭐ [`lab-log.zh.md`](lab-log.zh.md) | **实测记录**（最值钱的一份）：20/20 全是 7 · 三种 dollars · 两次分母攻击 · Mood Ring 五版演化与 2/5 · 20 发攻防 · `vault.py` · k-means 未标准化 |
| ⭐ [`delta.zh.md`](delta.zh.md) | **幻灯片增量**：6 道随堂测验（含答案）· Round 1/2 标准答案 · 停课规则 · Act V 谜题真实数据 · p92 填好的地图 |
| [`notes.zh.md`](notes.zh.md) | **现场笔记**：口头增量（encode/decode · 母语是向量 · scaling laws · InstructGPT · system/user prompt） |
| [`attack-dilution.txt`](attack-dilution.txt) | 那份 700 词的间接注入档案（Act VI 用） |
| [`the-literal-genie-of-the-strange-lamp (1).pdf`](the-literal-genie-of-the-strange-lamp%20(1).pdf) | **幻灯片原件**（101 页） |
| [`strange-lamp/`](strange-lamp/) | 实验 app（`uv run strange-lamp` → localhost:8501） |
| [`uploads/`](uploads/) | 讲义 PDF、app 截图，命名沿用 `slide-NN-xxx.png` |
| 📚 [`../reading-list.zh.md`](../reading-list.zh.md) | 论文清单（全课程共用） |

## 全天七幕

| 时间 | 幕 | 灯的面孔 | Lab / 体验 |
| --- | --- | --- | --- |
| 11:00–11:15 | Prologue · Rub the lamp again | 再次被擦亮 | Say-it-back（凭记忆重建 Week 1 地图） |
| 11:15–12:10 | **I · What have I left unsaid?** | 沉默：被众数填满 | Model Parliament；Lamp of Images |
| 12:10–13:20 | **II · The Literal Genie** | 顽皮 | The Literal Genie；Hall of Loopholes |
| 13:20–14:15 | *lunch* | | |
| 14:15–15:05 | **III · COSTAR** | 被模板化 | 分类练习；Civitai showcase |
| 15:05–16:15 | **IV · Old Faithful** | 上岗干活 | Old Faithful（真实数据） |
| 16:15–16:30 | *break* | | |
| 16:30–17:30 | **V · Reverse the Oracle** | 被逆向工程 | Reverse the Oracle（分组） |
| 17:30–18:40 | **VI · The Vault** | 被攻击 | The Vault（team vs team） |
| 18:40–19:15 | **Coda · The Honest Genie** | 诚实 | Honest Genie；Model Parliament |
| 19:15–19:30 | Buffer | | 提问；take-home |

> 一盏灯，一整天。每幕结尾都留下同一种未言明的挫败——**judged by feel, and felt the want of a ruler.**
> 讲义：*"That frustration is not a gap in the day; it is its destination."*

## 本周要带走的能力（讲义 "What Must You Carry Forward"）

- [ ] 说清为什么 prompt 是**部分规格说明**：每个没写的细节 = 一个自由度 = 一次先验填充
- [ ] 在自己的 prompt 里认出日常语言藏起来的沉默：单位、日期惯例、敬语等级、"top"和"Q3"的定义、参照系
- [ ] 把 prompt 当**合同**而非暗示；交给 agent 的目标是**带牙齿的合同**
- [ ] 说出**规格博弈 / reward hacking** 的名字：满足字面、背叛精神 = 微缩版对齐问题
- [ ] 用六件套给愿望防精灵：constraints / output format / 正反例 / guardrails / acceptance criteria / escape hatch
- [ ] 把 COSTAR 当**对抗沉默的检查清单**——并知道**任何模板的列都装不下什么**
- [ ] 在升级阶梯上给 prompting 定位：`prompt → examples → retrieval → adapter(LoRA) → full fine-tune`
- [ ] 在真实数据上对比裸提示 vs COSTAR 提示，并说出**哪个答案你敢贴出去**
- [ ] 说清手写 prompt 为什么**过拟合示例**，以及这个失败如何催生"想要一个分数 + 一次搜索"
- [ ] 说清纯 prompt 防御为什么必漏，并说出 **lethal trifecta**
- [ ] 把精灵掉转过来：让模型在行动前先说出你漏说了什么

## 课前环境（11:00 前）

| 步骤 | 命令 / 动作 | 状态 |
| --- | --- | --- |
| 1 | 装 `uv`：`curl -LsSf https://astral.sh/uv/install.sh \| sh`（Mac，装完重开终端） | ⬜ |
| 2 | **拿到 `strange-lamp.zip`** ← 讲义说从 *course portal* 下载，暂未找到 | ⚠️ **未解决** |
| 3 | `cd strange-lamp && uv sync && uv run strange-lamp` → http://localhost:8501 | ⬜ |
| 4 | OpenRouter key（https://openrouter.ai/keys，几美元够一天）→ sidebar 或 `.env` 的 `OPENROUTER_API_KEY=` | ⬜ |

> 免费模型每分钟只允许几次请求，一整天的 lab 用付费模型顺很多（每次许愿几分之一美分）。
> 每个回答都带一个**标明模型名的小徽章**——今天好几道题就是在问"换一个精灵会不会找到不同的缺口"。
> Setup 卡住不要慌：每个 demo 投影仪上都会跑一遍。

**App 七个 Tab**：The Literal Genie · The Honest Genie · The Lamp of Images · Old Faithful · Reverse the Oracle · The Vault · Model Parliament（一个 prompt，最多四个模型同时跑）

## 待确认清单（听课时对照）

- [ ] 随机数实验：**我们这屋**真的最爱选 7 吗？模型呢？（blue-seven 现象）
- [ ] 图像模型今天把 6:37 的钟画成几点？红酒停在哪？左撇子要几轮/几个词才画对？
- [ ] 改写过的外科医生谜题——模型读**写着的字**，还是答那个听过一千遍的谜题？
- [ ] Round 2 八张愿望卡里，**哪一张是真实生产事故**（讲义说"至少有一个"）？
- [ ] Round 3 绑住精灵的**最少追加词数**是多少？（作业目标 < 40 词）
- [ ] "给精灵装上手"之后重跑"周一前砍一半云账单"——它到底做了什么？
- [ ] Old Faithful：COSTAR 版跨模型的**一致性**是否真的更高？（scope / format 收敛）
- [ ] Vault 复盘：我们的金库占了 lethal trifecta 三样里的哪两样？第三样会加上什么？
- [ ] 最终假说是否成立：**"prompt 越好，模型越不重要"**

## 作业（take-home）

1. 写完 **Old Faithful 的 COSTAR prompt**，三个模型各跑一遍 → 哪个答案敢贴上护林员告示牌？
2. 带上最好的 **Oracle prompt** —— **以及它在隐藏测试上的失败**。它是下周优化器的**种子**。
3. 选做：用 **< 40 个追加词**绑住 Round 2 的某个愿望。
4. 选做：*Is Prompt Engineering Dead?* —— 用 `openai/gpt-astra-latest` 做公平测试（关掉精灵、裸问、再让它坦白）。

## 必读

| 文献 | 为什么 |
| --- | --- |
| Sheila Teo, *How I Won Singapore's GPT-4 Prompt Engineering Competition* | COSTAR 的出处；**Act III 之后**读，注意里面有多少是在关掉沉默 |
| Krakovna et al., *Specification Gaming: The Flip Side of AI Ingenuity* | 字面精灵的学名与案例库；reward hacking 是普遍现象不是奇闻 |
| Clark & Amodei, *Faulty Reward Functions in the Wild* | CoastRunners 赛艇——"达标却脱靶"最干净的一张图 |
| Simon Willison, *The Lethal Trifecta for AI Agents* | 精灵有手之后 Vault 为什么要紧；**造读不可信内容的 agent 之前必读** |

**Oliver Twist 选读**（通向下周）：Azzalini & Bowman (Old Faithful) · **DSPy** · **GEPA** · **LoRA**

## 下周

**自动提示词优化** —— DSPy、MIPROv2、GEPA。
你带回去的 Oracle prompt 变成种子，**prompt 不再是写出来的，而是编译出来的**。

## 相关

- 前置：[`../ai-agents-week-01/index.md`](../ai-agents-week-01/index.md)（agent 的定义 / 记忆三分法）
- 前置：[`../ai-agents-week-00/summary.zh.md`](../ai-agents-week-00/summary.zh.md)（**loop / governor / verifier / doom loop** —— 序幕要凭记忆复述的就是这张图）
- Week 00 的灯：[`../ai-agents-week-00/uploads/slide-09-aladdin-lamp.png`](../ai-agents-week-00/uploads/slide-09-aladdin-lamp.png)（ACT I，delegation 的最古老形态 —— **今天这盏是同一盏**）
