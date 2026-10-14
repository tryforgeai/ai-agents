# AI Agents Week 04 笔记 — Skillcraft（续）

日期：2026-10-11
来源：沿用 Week 03 的 lesson plan 和 `skillcraft-slides.pdf`，**上周讲了一部分，本周继续**（页码为幻灯片右下角编号）
状态：课堂速记，记本周实际讲到的页、课堂问答与补充例子；deck 的完整逐幕整理见 [Week 03 notes](../ai-agents-week-03/notes.zh.md)

---

## 今天走过的页

| 页 | 标题 | 一句话 |
| --- | --- | --- |
| p.6 | Prologue · 1707 — Nobody knew where they were | Scilly 海难；1714 年悬赏 £20,000 求海上经度 |
| — | Four machines — Each one proved the last incomplete | H1→H4，每台建在上一台的做法上，又证明它不够 |
| p.14 | *"Mastery is a library of procedures — each one learned by finding the last one broken."* | 今日主线：Skills |
| p.16 | Agent, tool, or skill? | "a genuinely slippery distinction" |
| p.17 | The Trinity, Resolved | tool = 单次调用；skill = 打包的 procedural knowledge；agent = 带 agency 的 tool（循环、自主、选择）。**skill 介于 prompt 和 program 之间** |
| p.19 | Four verbs | Authored / Retrieved / Composed / Improved |
| p.21 | Progressive disclosure | L1 metadata 常驻约 100 tokens；L2 body 相关时加载；L3 files 按需读取 |
| p.32 | Irrelevant context is not free | 示意模型 a(n) = a₀e^(−λn)；"全部加载"落在曲线最右端 |
| 白板 | 注意力 + 背包 | 见下节 |
| p.38 | A calculus of skills | β_A ⟸ β_B ∧ β_C ∧ (A's own checks) |
| p.44 | Voyager — a growing skill library | 自动课程 / 代码技能库（embedding 检索）/ self-verification |
| p.69 | Act V · Design Patterns | 开始讲模式 |
| p.72 | Structural — How a skill is shaped | 六个结构模式（见下表） |
| p.73 | 1/6 Lean Core + Appendix（"the master pattern"） | 正文只放主路径，其余放一行指针后的 L3 文件 |
| p.74 | 2/6 Single Canonical Source | 一个流程只有一个家，其他 skill 引用或组合 |
| p.75 | 3/6 Checklist-Carrier | 让 agent 把清单抄进回复、边做边勾；termination β 变得可见 |
| p.76 | 4/6 Template-Bearer | 精确格式打包成 L3 模板文件，正文只负责填空；格式变成确定性的 |
| p.77 | 5/6 Progressive-Disclosure Ladder | 常见情况放正文，每个罕见分支一个文件："for X, read x.md"；平均加载成本贴近最小值，覆盖仍完整 |
| p.78 | 6/6 Front-Matter Contract | frontmatter 是 router / index / security 实际读的东西，要当严格合同写 |
| p.79 | Behavioural — How a skill decides & acts | 四个行为模式：Pushy Trigger / Definition-of-Done / Guardrail / Router |
| p.80 | Compositional — How skills combine | Skill-of-Skills / Pipeline / Skill + MCP / Subagent-backed；"Closure of options under hierarchy — kept honest by clean termination." |
| p.81 | A Pattern Up Close — Dry-Run / Preview | 后果重、难撤回的动作：先预览"会做什么"，确认后才执行；幂等的程序性表亲 |
| p.82 | The Shadow — Anti-patterns & smells | 五种坏味道，每一种都对应 Act II 公式 VoL(s) = pₛ·gₛ − κ(cₛ) 里的一个量 |
| p.83 | Reach for the Right Shape — Problem → pattern | 按问题查模式的速查表 |
| p.84 | Act V · Pop Quiz 5 — four skills, four shapes | 退款 / "report" 撞车 / 精确版式 / 不报旧价，各对应一个模式 |
| p.86 | Milestone · Act VI — Synthesis | architecture, and where it leads |
| p.87 | The Blueprint — A skill-rich agent system | 七个部件 + 四个关注点分开：access · procedure · selection · governance |
| p.88 | One Picture — Five sides of one discipline | Tools / MCP / RAG / Memory / Skills，全部都是 context engineering |
| p.89 | Prefer the Cheapest Sufficient Layer — The escalation ladder | prompt → prompt-opt → RAG → SFT → RL；只在必须时往上爬，skill 在低、可撤回的那几级 |
| p.90 | Where an Organization's Competence Accrues — A skill maturity model | 0 Ad hoc → 1 Authored → 2 Curated library → 3 Evaluated & governed → 4 Self-improving；关键一跳是 2 → 3 |
| p.91 | The Common Thread — Impact, in one shape | 四类案例，同一个形状：把反复出现的"怎么做"变成一个可检查、可检索、可改进、按需加载的文件 |
| p.92 | Act VI · Pop Quiz 6 — the team that wants to fine-tune | 十二步月结：先写 skill，只在没见过的案例上持续失败时才往上爬 |
| p.93 | Quiz 6 — answered | 官方答案与笔记一致 ✅ |
| p.94 | Closing — The library and the lifelong agent | 手艺是手手相传的流程；skill 是第一个由机器持有、用我们的语言阅读的成员；"a Library of Alexandria that tends its own shelves" |
| p.96 | Act VI · Say It Back — The map, filled | 八个故事 / 练习各教了什么（复习总表） |
| p.98 | Promises Kept · 1 of 3 — The WHY | 每次重新推理 = 一串猜测：10 步 × 90% ≈ 35%；"Don't make the model rediscover what you already know." |
| p.99 | Promises Kept · 2 of 3 — The WHAT | skill = 文件夹：description（何时）+ procedure（怎么做）+ Done when + scripts，相关时才加载；"A skill is a prompt that waits in the pantry." |
| p.100 | Promises Kept · 3 of 3 — The HOW | 五条做法；"Then find out where yours breaks — tonight." |
| p.101 | Milestone · Coda — Hokusai at Seventy-Three | 说自己前七十年的画都不算数的大师 |
| p.102 | Coda · 1834 — A postscript to Mount Fuji | 《富岳百景》跋：六岁起画，七十岁前不值一提，七十三岁才"开始"懂；署名"画狂老人" |
| p.103 | Coda · Dusk — Understanding arrives late | 黑格尔：密涅瓦的猫头鹰黄昏才起飞；"Every stage of mastery is the vantage point from which the last one looks broken." |
| p.104 | Milestone · The Lab — An Appointment in Samarra | 晚间 Lab 开场：一个注定会发生的约会，在对的城市、对的时间 |
| p.105 | The Lab · The Story — The servant in the market | 仆人把死神的手势读成威胁，借主人的马逃往萨马拉；"Where Death will not find him — he thinks." |
| p.107 | The Lab · Tonight's Wish — "Just put it on my calendar." | 一句话，200 个示范（看 100、扣 100），三层；"It looks like one step. It is more than ten." |
| p.113 | Appendix · Flyover Territory — Self-Evolving Skills | 前沿内容，本周只"飞过"；提示词优化那几周正式讲 |
| p.114 | What Changes? — Three kinds of evolution | 改权重 / 改上下文和 skill / 两者一起；"A skill is the cheapest unit of evolution — a bad one is undone with git revert." |
| p.116 | Why Keep the Whole Frontier? — Dominance, made precise | Pareto 支配的定义；只留平均最好的，会丢掉你最想拿来繁殖的边缘专家 |
| p.118 | The Half-Life Fallacy — "RL is dead because of GEPA"? | 技术不会死，只会被重新分配到更难的问题上 |

⚠️ p.44 → p.69 之间（Act III 后半、Act IV Practice）本周没有截图记录，可能快速带过；复习时看 Week 03 notes 对应部分。

---

## 白板：为什么无关上下文有成本

- **A = softmax(⟨K,Q⟩ / √d) · V**。softmax 让所有 token 的权重总和为 1，注意力是固定预算；无关 token 越多，相关内容分到的份额越少 → p.32 曲线的直觉来源。
- **Knapsack**：上下文窗口是容量有限的背包，memory、skill、工具结果都在抢位置 → 对应 VoL(s) = pₛ·gₛ − κ(cₛ)。
- **θ → response**：权重固定，harness 能控制的只有背包里装什么（context engineering）。

## p.38 组合演算

- β 来自 options 框架（Sutton, Precup, Singh 1999）的 termination，对应 skill 的 **Done when**。
- 父 skill 完成 = 子 skill 都完成 **且** 父 skill 自己的检查通过。最容易漏的是 "A's own checks"（如：时区换算、`.ics` 都对，但和日历冲突）。
- 能力复利，错误也复利：每步 95% 成功率，串 3 步 ≈ 86%，串 10 步 ≈ 60%。

## p.72 六个结构模式

| 模式 | 含义 |
| --- | --- |
| Lean Core + Appendix | 主路径在正文，其余推迟 |
| Single Canonical Source | 一个家，不漂移 |
| Checklist-Carrier | 长流程自带清单、自我监控 |
| Template-Bearer | 精确格式直接打包 |
| Progressive-Disclosure Ladder | 每个罕见分支一个指针 |
| Front-Matter Contract | metadata 当严格合同（name 与目录同名 ≤64 字符；description ≤1,024 字符、无尖括号） |

两组：控制上下文成本（Lean Core、Ladder）；减少模型自由发挥（其余四个）。

---

## 课堂聊天问答：记忆的分类

- Vinoo 问：除了 semantic / procedural / episodic，还有 operational memory 吗？Dishant：**operational memory 即 working memory**。
- Vinoo 追问：operational 和 procedural 是一回事吗？Dishant：**不是**。working memory 是当前 agent session 完成任务所需的内存，包括管理上下文（部分内容移出窗口、暂存再放回）和本次会话里用户提到的偏好（如某种写测试的方式）；Asif 会在后续课程细讲。

| 记忆 | 管什么 | agent 里的对应 | 时间尺度 |
| --- | --- | --- | --- |
| Working | 现在手里拿着什么 | 上下文窗口 | 本次 session |
| Episodic | 发生过什么 | trace、Reflexion 的失败反思 | 长期 |
| Semantic | 知道什么 | 事实、用户画像、RAG | 长期 |
| Procedural | 会做什么 | skill、Voyager 技能库 | 长期 |

**procedural memory 是 skill 吗？** 大体是：p.17 原文就说 skill 是 "packaged procedural knowledge"。但不完全等同：模型权重里隐含的做法也是 procedural，却不是 skill；人手写的 skill 更像预装手册，只有 agent 从经历中提炼的 skill（Voyager、自进化 skill）才真正像"记忆"。渐进加载 = 决定哪些 procedural memory 何时搬进 working memory。

---

## 补充例子：三个结构模式写进同一个 skill

> 以晚间 Lab 的 `when-the-time-is-right` 为例。**具体规则为示意，不是 kit 原文。**

### 目录

```
when-the-time-is-right/
├── SKILL.md                 ← Lean Core：只有主路径和清单
├── references/
│   ├── timezones.md         ← Appendix：跨时区时才读
│   ├── holidays.md          ← Appendix：周末或节假日时才读
│   └── ics-format.md        ← Appendix：生成失败时才读
└── scripts/
    └── make_ics.py

（共享，不在这个 skill 里）
owner/profile.md             ← Canonical Source：Zara 的规则只存在这里
skills/timezone-convert/     ← Canonical Source：时区换算只有这一份
```

### SKILL.md

```markdown
---
name: when-the-time-is-right
description: Turn a forwarded meeting message into a calendar invite (.ics).
  Use when the user says "put it on my calendar", "add this to my calendar",
  or forwards a meeting message asking to schedule it. Do not use for sending
  invites, editing existing events, or general time questions.
---

# When the Time Is Right

开始前，把下面的清单原样复制到你的回复里。每完成一项改成 [x]；
不适用写 [n/a] 并说明原因。不要跳项。

## Checklist
- [ ] 1. 提取日期、时间、时长、参会人、地点
- [ ] 2. 缺日期或时间？→ 只问一个问题，然后停
- [ ] 3. 判断时区。出现两个以上时区或参会人在外地
        → 使用 `timezone-convert` skill 换算；细则见 `references/timezones.md`
- [ ] 4. 日期是周末或可能是节假日 → 读 `references/holidays.md`
- [ ] 5. 读 `owner/profile.md`，检查 Zara 的规则（不要凭记忆）
- [ ] 6. 检查与 `owner/calendar.ics` 是否冲突
- [ ] 7. 运行 `scripts/make_ics.py` 生成邀请；失败时读 `references/ics-format.md`
- [ ] 8. 重读生成的 .ics，核对时间与第 3 步结果一致
- [ ] 9. 只输出一种结果：.ics / 无法安排的说明（附可行时间）/ 一个问题

## Done when
- 清单每一项都是 [x] 或 [n/a]
- 输出恰好是第 9 步三种结果之一
- .ics 里的时间来自脚本，不是心算
```

### 每一处用的是哪个模式

| 位置 | 模式 | 作用 |
| --- | --- | --- |
| 正文只有清单和 Done when，约 35 行 | Lean Core | 普通请求加载便宜 |
| 第 3、4、7 步"遇到 X → 读 Y" | Appendix 指针 | 罕见分支走到了才付费 |
| 第 3 步调用 `timezone-convert` | Single Canonical Source | 时区逻辑只有一份，修一次全部生效 |
| 第 5 步读 `profile.md`，"不要凭记忆" | Single Canonical Source | 规则不复制进 skill，避免漂移 |
| 开头"复制到回复里" + `[ ]` 清单 | Checklist-Carrier | 长流程自我监控，不漏第 5、6 步 |
| Done when 引用清单 | β 可见 | 终止条件 = 全部打勾 |

### agent 做到一半时的回复（Checklist-Carrier 的效果）

```
- [x] 1. 提取：10/16 周五 15:00，30 分钟，Priya，Zoom
- [n/a] 2. 日期和时间齐全
- [x] 3. Priya 在班加罗尔 → 换算为 PDT 02:30 ← 注意
- [x] 4. 非节假日
- [x] 5. 日历无冲突
- [ ] 6. ← NOW：凌晨 2:30 违反 Zara 的规则吗？
- [ ] 7.
- [ ] 8.
- [ ] 9.
```

没有清单时，agent 很可能换算完就直接生成 `.ics`，格式全对，却约在凌晨两点半。

### 写的时候注意

- **清单留在正文**，它是主路径，每次都用；不要推到附录。
- **指针要写触发条件**："遇到 X 时读 Y"，而不是"参见附录"。太模糊会 Silent（该读不读）或每次都读（等于没拆）。
- **抄进回复为什么有效**：`SKILL.md` 里的清单会随对话沉进上下文中段（p.32 的低召回区）；每次打勾都把清单重写到末尾，等于用输出刷新 working memory。
- **共享即耦合**：`timezone-convert` 一改，所有引用它的 skill 都受影响，它需要自己的测试。

---

## p.76 Template-Bearer

- **Problem**：输出必须精确（报表版式、信件、JSON schema），散文描述太松，钉不住。
- **Fix**：把字面模板打包成 Level-3 文件，正文只说"填这个模板"。
- **Payoff**：格式变成确定性的，也不必在正文里花 token 描述格式。

例子（晚间 Lab）：

```
when-the-time-is-right/
├── SKILL.md            ← "第 7 步：填 templates/invite.ics，或运行 make_ics.py"
└── templates/
    └── invite.ics      ← 字面模板
```

```
BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART;TZID={{tzid}}:{{start}}
DTEND;TZID={{tzid}}:{{end}}
SUMMARY:{{title}}
ATTENDEE:mailto:{{attendee}}
END:VEVENT
END:VCALENDAR
```

### 例子 2：客户邮件 → 工单 JSON（给下游系统读）

**改之前（散文描述格式）**：正文写"输出 JSON，包含优先级、类别、摘要、客户邮箱"。跑十次会看到：

```
{"Priority": "High", ...}            ← 键名大小写不一
{"prio": "P1", "category": ...}      ← 键名和取值都漂了
```json\n{...}\n```                    ← 多了 markdown 围栏，下游解析失败
"好的，这是工单：{...}"              ← 前面多一句话
```

**改之后（Template-Bearer）**：

```
email-to-ticket/
├── SKILL.md                ← "按 templates/ticket.json 填写；只输出 JSON 本身"
├── templates/ticket.json   ← 字面模板
└── scripts/validate.py     ← 按 schema 校验，不通过就返工
```

```json
{
  "priority": "{{P1|P2|P3}}",
  "category": "{{billing|access|bug|feature}}",
  "summary": "{{≤ 80 字}}",
  "customer_email": "{{email}}"
}
```

- 键名、取值范围、长度上限都写死在模板里，模型只能填空。
- 正文的 Done when："`validate.py` 返回 OK"——模板管格式，脚本管验证。
- 换下游字段时只改模板一个文件（同时也是 Single Canonical Source）。

要点：

- **模板钉住的是格式，不是值。** 字段齐了，`{{start}}` 填错时区照样是错的 → 值要由第 3 步的脚本给出，第 8 步再核对。
- **能用脚本渲染就别让模型填。** 模板 + `make_ics.py` 渲染比模型手抄更稳（Run, Don't Reason）；模型只负责把提取出的字段交给脚本。
- **和 Lean Core 的关系**：模板放 L3，只有走到输出那一步才读，正文不为格式付费。
- 对照 `paper-deep-read`：`reference-talk-outline.md` 就是一个 Template-Bearer。

---

## p.77 Progressive-Disclosure Ladder

- **Problem**：简单的常见情况后面拖着一条长尾——大量罕见、细节很多的子情况。
- **Fix**：核心处理常见情况；每个罕见分支命名一个文件：**"for X, read x.md"**。
- **Payoff**：平均加载成本贴近常见情况的最低值，覆盖仍然完整。
- 与 Lean Core 的区别：Lean Core 是"正文只放主路径"的原则；Ladder 是把长尾**按分支拆成一档一档**，按频率排列，一个分支一个文件。

### 例子：PDF 提取 skill（幻灯片里 forms / tables / scanned 那一排）

```
pdf-extract/
├── SKILL.md         ← 常见情况：普通文字型 PDF，直接抽文本
├── forms.md         ← 有可填写表单字段
├── tables.md        ← 要把表格抽成结构化数据
├── scanned.md       ← 扫描件 / 图片型，需要 OCR
├── encrypted.md     ← 有密码保护
└── scripts/extract_text.py
```

```markdown
## Procedure
1. 运行 `scripts/extract_text.py <file>`，输出文本。
2. 按情况分流（只读命中的那一个）：
   - 有可填写表单字段 → 读 `forms.md`
   - 用户要表格 / 结构化数据 → 读 `tables.md`
   - 第 1 步抽出的文本为空或乱码 → 很可能是扫描件，读 `scanned.md`
   - 打开时报加密错误 → 读 `encrypted.md`
3. 以上都不是 → 直接返回第 1 步的文本。

## Done when
- 返回了文本或结构化结果；或说明了为什么抽不出来。
```

**加载成本（数字为示意）**

| 文件 | tokens | 出现频率 |
| --- | --- | --- |
| SKILL.md | 400 | 100% |
| forms.md | 800 | 10% |
| tables.md | 1,000 | 8% |
| scanned.md | 1,200 | 5% |
| encrypted.md | 500 | 2% |

- 全塞正文：每次 400 + 800 + 1,000 + 1,200 + 500 = **3,900**
- Ladder：平均 400 + 0.10×800 + 0.08×1,000 + 0.05×1,200 + 0.02×500 = **630**
- 七成请求只付 400；碰到扫描件那一次付 1,600，但覆盖一样完整。

**写好阶梯的三个要点**

- **触发条件要能观察到**："文本为空或乱码"是 agent 自己能看到的信号，比"如果是扫描件"好判断。
- **分支互斥、各读各的**：一个请求通常只读一档；需要两档（扫描件里的表格）时允许叠加读。
- **按频率排**：高频分支放前面，新出现的罕见情况直接加一档文件，不动正文。

---

## p.78 Front-Matter Contract

```yaml
---
name: invoice-filler
description: Fills vendor invoices…
version: 2.1.0
allowed-tools: [Read, Write]
---
```

| 字段 | 谁读 | 作用 |
| --- | --- | --- |
| `description` | **Router** | 选不选它（要有区分度：做什么 / 何时用 / 何时不用） |
| `name` + `version` | **Index** | 编目、版本管理（语义化版本） |
| `allowed-tools` | **Security** | 沙箱：这个 skill 最多能碰什么 |

- **Problem**：metadata 才是 runtime 和 router 真正读的部分，却总是最后才随手补上。
- **Fix**：把 frontmatter 当严格合同：有区分度的 description、语义化版本、声明可以触碰的工具。
- **Payoff**：可被选中、可治理、可沙箱化——合同正好是索引和安全审查要读的东西。

⚠️ **与晚间 Lab 的兼容约束不冲突但要分清**：Lab 要求 front matter **先只用 `name` 和 `description`**，为了在 Hermes 与 Claude Desktop 都能加载。`version`、`allowed-tools` 是否被识别取决于客户端，用之前先查该客户端支持哪些字段。

**`allowed-tools` 的意义**：上周市场插曲讲过，第三方 skill 同时带来指令和代码两类攻击面。声明 `[Read, Write]` 就等于告诉审查者和 runtime："它不需要网络、不需要 Bash"——超出声明就是红旗。

### 例子：同一个 skill 的 frontmatter，随手写 vs. 当合同写

**随手写（最后才补）**

```yaml
---
name: Calendar Helper
description: Helps with calendar stuff.
---
```

- `name` 有大写和空格，和目录名 `when-the-time-is-right` 不一致 → 打包 / 加载失败（Front-Matter Contract 的硬规则）。
- description 没有区分度：Router 碰到"现在几点""帮我改会议""发邀请给 Priya"都可能选它（God-Skill / Collision）。
- 没有版本、没有工具声明 → Index 无法管理，Security 无从审查。

**当合同写**

```yaml
---
name: when-the-time-is-right
description: Turn a forwarded meeting message into a calendar invite file
  (.ics), or explain why it cannot be scheduled, or ask one clarifying
  question. Use when the user says "put it on my calendar", "add this to my
  calendar", or forwards a meeting message asking to schedule it. Do not use
  for sending invites, editing or deleting existing events, or general
  time and date questions.
version: 1.2.0
allowed-tools: [Read, Write, Bash]
---
```

| 部分 | 给谁 | 写了什么 |
| --- | --- | --- |
| `name` | Index | 小写 + 连字符，与目录同名，≤64 字符 |
| description 第 1 句 | Router | **做什么**：三种输出（.ics / 说明 / 一个问题） |
| description "Use when…" | Router | **何时用**：用户真会说的原话 |
| description "Do not use…" | Router | **何时不用**：发送邀请（Dry-Run 边界）、改已有事件、一般时间问题 |
| `version: 1.2.0` | Index | 语义化版本：改规则行为升 minor，改输出格式升 major |
| `allowed-tools` | Security | 读 profile / 日历、写 .ics、跑 `scripts/`；**没有网络** → 不可能"顺手发出邀请" |

⚠️ 晚间 Lab 打包时先删掉 `version` 和 `allowed-tools`，只留 `name` + `description`，确保 Hermes 与 Claude Desktop 都能加载。

**对照自己的 `paper-deep-read`**：description 已经符合合同——做什么（论文 → 中文精读笔记，输出到 vault）、何时用（「精读」「读一下这篇」「照老规矩整理」等原话）、何时不用（摘要、单个问题、跨论文对比、课程讲义、翻译、纯 PDF 提取）都写全了；排除项里点名"那是课程周笔记"，正是防 Collision。可补的只有 `version`（若客户端支持），以及确认没有用到 `<` `>`。

---

## p.79 Behavioural — How a skill decides & acts

| 模式 | 一句话 | 解决什么 |
| --- | --- | --- |
| **Pushy Trigger** | 偏向触发（成本不对称） | 漏触发（Silent） |
| **Definition-of-Done** | 可检查的终止条件 | 不知道何时停 |
| **Guardrail** | 硬约束：先检查，违反就拒绝 | 不可违反的规则 |
| **Router** | 识别情况，分派给专门的 skill | 两个 skill 抢同一请求（Collision） |

**Pushy Trigger 的成本不对称**：该用没用 → 任务做错（贵）；不该用却加载 → 多付几百 token（便宜）。所以 description 宁可写得"积极"一点，多列用户原话。
- 前提是正文够瘦（Lean Core）：加载便宜，偏向触发才划算——两个模式是配套的。
- 和 p.32 不矛盾：p.32 反对的是"全部加载"，Pushy 只是在"相关与否拿不准"时倾向加载。
- 边界：积极 ≠ 什么都接。"Do not use…"仍要写，否则变成 God-Skill / Collision。

**课堂聊天（14:17）**：Vinoo 总结——清单可以是预先规定的，也可以按用例动态生成；关键是**始终有一份清单并始终放在上下文里**（2 个 👍）。
补充：动态清单可以，但 skill 里写死的**必经检查点**不能被动态规划删掉——那些正是"上次坏在哪里"学来的步骤。

**p.80 底部那句**："…inside a skill. *Closure of options under hierarchy — kept honest by clean termination.*"
- 回扣 p.38：skill 可以在 skill 里面调用 skill（options 在层级下封闭），结构不变；
- 但前提是每一层都**干净终止**——子 skill 的 β 必须可检查、不悬空，父 skill 才敢继续，并且父 skill 仍要做自己的检查。
- "kept honest"：没有干净终止，层级组合就会"撒谎"——上层以为下层完成了，其实没有。

---

## p.80 Compositional — How skills combine

| 模式 | 一句话 | 例子 |
| --- | --- | --- |
| **Skill-of-Skills** | 编排者点名调用子 skill | `when-the-time-is-right` 调用 `timezone-convert` |
| **Pipeline** | 固定顺序的一串变换 | 提取 → 换算 → 查冲突 → 生成 .ics |
| **Skill + MCP** | skill 给流程，MCP 给访问能力 | skill 写"怎么排会"，日历 MCP 负责读写真实日历 |
| **Subagent-backed** | skill 内部开一个有边界的子 agent | 把"在 50 封邮件里找会议线索"交给子 agent，只收回结论 |

- Skill-of-Skills 由编排者**动态选择**；Pipeline 是**顺序写死**。步骤固定用 Pipeline，要按情况挑用 Skill-of-Skills。
- Skill + MCP：procedure over access——MCP 回答"能碰到什么"，skill 回答"碰到之后怎么做"（呼应 p.17 的 tool / skill 分工）。
- Subagent-backed：bounded agency——子 agent 有自己的上下文窗口，脏活在里面做完，只把结果交回，不污染主上下文（p.32）；边界 = 允许的工具 + 必须交回的格式 + 终止条件。

## 课堂聊天：Vinoo 问 verifier（14:28，消息被截断）

"能否澄清 verifier？入口处有 verifier 吗（确认问题是……）"

我的理解：verifier 可以放在三处，正好对应 option 的三元组。

| 位置 | 对应 | 检查什么 | Samarra 的例子 |
| --- | --- | --- | --- |
| **入口** | initiation set *I* | 这个请求该不该由我处理？输入够不够？ | 不是排会请求 → 不触发；缺日期 → 问一个问题，停 |
| **每一步** | procedure 里的检查 | 这一步的输出对不对？ | 时区换算后核对；`.ics` 生成后重读 |
| **出口** | termination *β* | 整体完成了吗？ | 清单全勾；输出恰好是三种结果之一 |

- 入口检查分两层：**是不是我**（description / Router 决定，属 firing test 的范围）、**够不够做**（缺信息就问，不要猜）。
- Week 2 的 verifier 阶梯仍适用：同一 prompt 尾部检查 → 独立调用 → 不同推理基底 → 确定性 rubric；能写成十行代码的检查就放最上面那级。

---

## p.81 A Pattern Up Close — Dry-Run / Preview

用经典模式语言的四段式（Problem / Forces / Solution / Consequence）细讲一个模式：

- **Problem**：一个后果重大、难以撤回的动作。
- **Forces**：自主和速度 vs. 做错一次不可逆动作的代价。
- **Solution**：先预览它**将会**做什么；提交前要求确认。
- **Consequence**：错误在造成伤害前被拦住；它是**幂等性的程序性表亲**。

**例子（贷款，接 Vinoo 14:07 的问题）**

```markdown
- [ ] 4. 运行 `scripts/route.py <amount>`
- [ ] 5. 生成放款预览，**不执行**：
        金额 / 收款账户 / 利率 / 审批路径 / 将调用的 API
- [ ] 6. 把预览交给人确认；未收到明确的"确认"→ 停止
- [ ] 7. 确认后才调用放款 API，并带上 `request_id`
```

**"幂等的表亲"是什么意思**

| | 幂等（idempotency） | Dry-Run |
| --- | --- | --- |
| 层面 | 数据 / API | 流程 |
| 保证 | 同一操作做两次 = 做一次 | 真做之前先看一遍 |
| 防的是 | 重试导致重复执行（扣两次钱） | 第一次就做错 |

两者常一起用：预览防"做错"，`request_id` 幂等键防"确认后网络重试导致放款两次"。

**什么时候用**：发邮件、付款、删数据、改生产配置、对外发布。可撤回的动作（生成草稿、写本地文件）不必加，否则只是多一步打扰。

**晚间 Lab 本身就是 Dry-Run**：交付 `.ics` 文件，而不是直接发邀请——由 Zara 决定要不要用。

---

## p.82 The Shadow — Anti-patterns & smells

> **"Every smell points back to a Chapter-2 quantity."** —— Act II 的 VoL(s) = pₛ × gₛ − κ(cₛ)
> pₛ：被（正确）选中的概率；gₛ：加载后带来的能力收益；cₛ：占用的上下文；κ：上下文稀释成本。

| 坏味道 | 症状 | 坏在哪个量 | 解药（前面的模式） |
| --- | --- | --- | --- |
| **Kitchen-Sink** | 什么都塞进正文，没有渐进加载 | **cₛ 太大** → κ 吃掉收益 | Lean Core + Appendix、Ladder |
| **Silent** | 该用时从不触发 | **pₛ 太低** → 收益再大也乘以 0 | description 写用户原话、Pushy Trigger |
| **God-Skill** | 什么请求都接 | **pₛ 不加区分**：不相关时也触发，gₛ≈0 却付 κ | "Do not use…"、拆成多个 skill |
| **Collision** | 两个 skill 触发条件重叠 | **pₛ 被两个 skill 瓜分**，选错一个 gₛ 变负 | Router、互相写排除项 |
| **Stale** | 悄悄过期，规则已变 | **gₛ 随时间下降甚至变负**，pₛ 却还很高 | Single Canonical Source、`version`、发布后监控 |

- 读法：先看症状，再问"是哪个量坏了"，就知道该用哪个模式修。
- Stale 最危险：它照常触发、照常"完成"，错误不报警（对应 Week 03"发布后要记录是否触发、是否有帮助"）。
- Silent 和 God-Skill 是 pₛ 的两个极端；Pushy Trigger 往 God-Skill 那边推一点，"Do not use"再拉回来。

---

## p.83 Reach for the Right Shape — Problem → pattern（速查表）

| 遇到的问题 | 用这个模式 | 今天的例子 |
| --- | --- | --- |
| 罕见情况的长尾 | Progressive-Disclosure Ladder | PDF：forms / tables / scanned / encrypted |
| 输出格式必须精确 | Template-Bearer | `invite.ics`、工单 JSON |
| 不可违反的约束 | Guardrail + Escalation | 贷款 ≥ 100,000 → 人工审批 |
| 不可逆的动作 | Dry-Run + Idempotent | 放款预览 + `request_id` |
| 触发条件近似重复 | Router | 两个日历相关 skill 抢请求 |
| 需要外部数据 | Skill + MCP | skill 写排会流程，日历 MCP 读写 |

（截图底部可能还有未露出的条目。）

- 这张表是 p.82 的反面：p.82 从**症状**找坏掉的量，p.83 从**问题**找模式。
- ⚠️ Guardrail 一行：Week 03 课后修订——"绝对不能发生"的事要由 **hook** 在 harness 层强制，skill 正文里的 Guardrail 文字只是第二道防线。

---

## p.84 Act V · Pop Quiz 5 — four skills, four shapes

| 情况 | 模式 | 理由 |
| --- | --- | --- |
| (1) 给客户打退款 | **Dry-Run + Idempotent** | 动钱、不可逆；先预览，确认后带幂等键执行 |
| (2) "report" 同时唤醒 pptx 和 xlsx | **Router** | 触发条件重叠（Collision）；按格式线索分派 |
| (3) 发票必须匹配精确版式 | **Template-Bearer** | 格式必须一字不差 |
| (4) 绝不引用上季度价格 | **Guardrail + Escalation** | 不可违反的硬约束；拿不到当季价就停下上报 |

> **"A guardrail refuses what is forbidden; a dry-run shows what is about to happen, so a wrong but permitted action can still be stopped."**

guardrail 挡"被禁止的"，dry-run 挡"被允许但错了的"——退款给对的人、对的金额、但发错了账户，没有任何规则被违反，只有预览能让人看出来。
（答案与 Week 03 notes / 精读版一致。）

---

## p.86–87 Act VI · Synthesis — The Blueprint

> **Agent loop → retrieval / router → progressive-disclosure loader → the library and the tool / MCP layer, all under a governor, all watched by observability.**
> **Keep four concerns distinct: access · procedure · selection · governance.**

| 部件 | 做什么 | 今天对应的内容 |
| --- | --- | --- |
| Agent loop | 循环决定下一步 | p.17 agent = 带 agency 的 tool |
| Retrieval / router | 选哪个 skill | description、Pushy Trigger、Router、p.82 的 pₛ |
| Progressive-disclosure loader | 按层加载（metadata → body → files） | p.21、Lean Core、Ladder、p.32 的 κ(cₛ) |
| Library | 存放 skill | Voyager 技能库、Single Canonical Source、`version` |
| Tool / MCP layer | 真正触达外部世界 | Skill + MCP |
| Governor | 管住能做什么 | Guardrail、hook、`allowed-tools`、Dry-Run |
| Observability | 看见发生了什么 | 发布后记录触发 / 帮助 / 成本 / 冲突；防 Stale |

**四个关注点分开**

| 关注点 | 回答的问题 | 由谁负责 |
| --- | --- | --- |
| access | 能碰到什么？ | tool / MCP |
| procedure | 碰到之后怎么做？ | skill 正文 + scripts |
| selection | 这次该用哪个？ | description + router + loader |
| governance | 允许做什么、谁来审？ | governor（hook、权限、审批）+ observability |

- 混在一起的典型错误：把权限写进 skill 正文（governance 混进 procedure）；把流程写进 tool description（procedure 混进 access）；一个 description 什么都接（selection 失效 → God-Skill）。
- 读法：坏了一个地方，先问是四个中哪一个坏了，再去对应部件修。

---

## p.88 One Picture — Five sides of one discipline

| 部件 | 提供 | 早上的对应 |
| --- | --- | --- |
| Tools | capability（能做什么） | p.17 单次调用，input → output |
| MCP | access（能接到哪里） | tool 的接入标准 |
| RAG | facts（knowing-that） | semantic memory 的外部化 |
| Memory | the past（发生过什么） | episodic / working memory |
| Skills | procedure（knowing-how） | procedural memory |

> **All of them: context engineering — choosing what the model sees at each step.**

- 回到白板：θ 固定，harness 唯一能控制的是"背包里装什么"；softmax 让注意力是固定预算（p.32）。五样东西都在争同一个上下文窗口。
- 区别只在**放进去的是什么、什么时候放**：tool 的 schema 常驻；RAG 和 memory 按检索放；skill 按渐进加载放。
- 和 p.87 的四个关注点对照：Tools / MCP 管 access，Skills 管 procedure，RAG / Memory 是 procedure 运行时要的材料；selection 和 governance 横跨全部五样。

---

## p.89 Prefer the Cheapest Sufficient Layer — The escalation ladder

> prompt → prompt-opt → RAG → SFT → RL
> **"Sufficiency flows downward; necessity flows upward. Not a menu — a forced sequence. Climb only when you must. (Skills live at the low, reversible rungs.)"**

（p.89 在 p.86–88 之前先放过一次。）

**两句话怎么读**

- **Sufficiency flows downward**：低一级够用，就别往上——高的那级当然也能解决，但更贵、更难撤回。
- **Necessity flows upward**：只有低一级**被失败证据证明不够**，才有资格往上爬一级。
- **Not a menu**：不能因为"RL 听起来厉害"直接跳过去；必须按顺序，每一级都试过、失败了、有证据。

| 级 | 改的是什么 | 成本 | 能否撤回 |
| --- | --- | --- | --- |
| prompt / skill | 上下文里的文字 | 最低 | `git revert` |
| prompt-opt（DSPy / GEPA） | 让机器搜索更好的文字 | 低–中 | 仍是文字，可回退 |
| RAG | 按需取回的事实 | 中 | 换索引即可 |
| SFT | 模型权重 | 高 | 难，要回滚模型版本 |
| RL | 模型权重（按奖励） | 最高 | 最难 |

**用晚间 Lab 走一遍**

1. 日历 skill 在隐藏案例上失败 → 先看失败属于哪类：漏步骤 / 规则没写 → **改 skill**（第一级）。
2. 手改到第七版还在两个版本间摇摆 → **prompt 优化**："Tonight's skill becomes the baseline the optimizer must beat."（后续几周）
3. 失败是因为缺事实（各国节假日、Zara 的历史日程）→ **RAG**。
4. 只有当格式 / 判断方式反复修不好、且有大量标注数据 → 才考虑 **SFT / RL**。

- 和 Week 03 组织成熟度对应：先把做法写成 skill、整理成库、配上评测与治理，再谈自我改进。
- 和 Voyager 对应：改进积累在外部技能库（低级、可撤回），不更新权重。

---

## p.90 Where an Organization's Competence Accrues — A skill maturity model

> **0 Ad hoc → 1 Authored → 2 Curated library → 3 Evaluated & governed → 4 Self-improving**
> **"The jump that matters is 2 → 3: without eval and governance, a growing library is a liability."**

| 级 | 样子 | 问题 / 下一步 |
| --- | --- | --- |
| 0 Ad hoc | 每次临时写 prompt，做法在个人脑子里 | 不可复用，人走了做法也走了 |
| 1 Authored | 做法写成 skill 文件 | 单个可用，但散落各处 |
| 2 Curated library | 整理成库：命名、去重、Canonical Source | 越多越容易 Collision、Stale，没人知道哪个还管用 |
| 3 Evaluated & governed | 每个 skill 有 firing test + behaviour test；有权限、版本、审查、发布后监控 | 能证明"它有用、它安全" |
| 4 Self-improving | 根据失败自动改进 skill（Voyager、GEPA） | 必须先有第 3 级的 eval，否则自我改进没有方向 |

**为什么 2 → 3 最关键**
- 第 2 级的库越大，p.82 的坏味道越多：触发冲突、悄悄过期，而且没有人发现。
- 证据：SkillsBench——精选 skill +16.2 分，自生成 −1.3 分，2–3 个胜过 4 个以上。**差别在策展和评测，不在数量。**
- 第 4 级依赖第 3 级：GEPA 要读失败 trace 才能反思修改；没有 eval，就没有可读的失败。

**自查**：`paper-deep-read` 有 `tests/firing-tests.md`（firing test）+ `scripts/check_numbers.py`（behaviour 检查）→ 已经摸到第 3 级的门；缺的是 governance（版本、发布后记录触发与效果）。`when-the-time-is-right` 有 100 个公开案例 + `check.py`，但目前只测了脚本层，模型读取层的 behaviour test 还没跑。

---

## p.91 The Common Thread — Impact, in one shape

案例：transcript cleaner · document skills · coding-agent conventions · enterprise workflows

> **"In every case: a recurring *how* is lifted out of fallible repeated reasoning into an inspectable, retrievable, improvable artifact that loads only when relevant."**

逐词拆：

| 词 | 意思 | 今天对应 |
| --- | --- | --- |
| recurring *how* | 反复出现的"怎么做" | procedural knowledge（p.17） |
| fallible repeated reasoning | 每次重新推理，每次都可能错 | Run, Don't Reason；"漏第 4 步" |
| inspectable | 能读、能审 | 文件夹 + 文本；`allowed-tools`；Bazaar 审计 |
| retrievable | 能被找到 | description、Router（p.82 的 pₛ） |
| improvable | 能改进 | Improved（p.19）、版本、`git revert`、成熟度第 3→4 级 |
| loads only when relevant | 只在相关时加载 | 渐进加载（p.21）、κ(cₛ)（p.32） |

一句话把今天全天收成一个定义：**skill = 从"每次重新想"变成"写下来、找得到、改得了、用时才拿"。**

---

## p.92 Act VI · Pop Quiz 6 — the team that wants to fine-tune

> 一个团队想微调模型，好让 agent 遵循十二步月结流程。先试哪一级？什么证据能正当化往上爬？一句话说出阶梯的规则。

**参考答案（p.93 官方答案，与 Week 03 notes 一致 ✅）**：*"First a skill: the procedure written down, with scripts for the deterministic steps and a check at each step. Climb only if it keeps failing on cases it has not seen."*

展开：**先写 skill**——把十二步写下来（Checklist-Carrier），确定性步骤（对账、汇总、日期）交给脚本，每一步放检查，不可逆的过账走 Dry-Run。

**往上爬需要的证据**：在**没见过的**案例上**持续**失败，且失败原因不是 skill 能修的——

| 失败类型 | 先怎么修 | 仍失败才考虑 |
| --- | --- | --- |
| 漏步骤、规则没写 | 改 skill / 清单 | — |
| 手改版本间来回摇摆 | prompt 优化 | — |
| 缺事实（科目表、政策、上月数据） | RAG | — |
| 同类判断反复出错，且有大量已标注的历史月结 | — | SFT |

> **"Sufficiency flows downward: use the cheapest layer that works, and climb only when it demonstrably fails."**

- 为什么不该直接微调：十二步是**显式、固定、团队特有**的流程，正是 skill 最擅长的；微调把流程藏进权重，看不见、难审计、流程一改就要重训——而月结规则每年都会改。

---

## p.94 Closing — The library and the lifelong agent

> *"A craft was always a procedure passed hand to hand. A skill is the newest member of that lineage — the first whose holder is a machine that reads it in our own words."*
> **"We have, for the first time, a Library of Alexandria that tends its own shelves."**

- 第一句：从学徒制、手册、runbook 到 skill，都是"做法的传承"；新的地方是持有者是机器，而载体仍是**人能读的文字**（inspectable，p.91）。
- 第二句：亚历山大图书馆 = 收集一切知识的库；"自己整理书架" = 成熟度第 4 级 Self-improving（Voyager 的技能库、附录的自进化 skill / GEPA）。
- 我的批注：书架能自己整理的前提是第 3 级——有评测才知道哪本该留、哪本该撤（SkillsBench：自生成 −1.3，精选 +16.2）。否则就是 p.90 说的 liability。
- 回扣开场：p.14 *"Mastery is a library of procedures — each one learned by finding the last one broken."* 开场是人的图书馆，结尾是机器的图书馆。

---

## p.96 Act VI · Say It Back — The map, filled（复习总表）

| 故事或练习 | 它教了什么 | 中文 |
| --- | --- | --- |
| Harrison's clocks | skills accumulate; each artifact shows the last incomplete | 技能会积累；每一件新作品都暴露上一件的不足 |
| The Literal Cook | a procedure is read literally — say how, and when to stop | 流程会被逐字执行——要写清怎么做、何时停 |
| Which Scroll Wakes? | the description is the trigger, and it overfits its examples | description 就是触发器，而且会过拟合你给的例子 |
| The loading rule | relevance must outweigh dilution; Level 1 makes relevance cheap | 相关性收益必须大于稀释成本；Level 1 让判断相关性变便宜 |
| Voyager | a library grows by keeping what works, after checking it | 技能库靠"验证过才保留"来增长 |
| The marketplace | a stranger's skill is untrusted code plus instruction | 陌生人的 skill = 不可信的代码 + 指令 |
| The shampoo bottle | no definition of done, no skill | 没有 Done when，就不算 skill（"搓、冲、重复"永远停不下来） |
| The escalation ladder | climb only when the cheaper layer fails | 便宜的那层失败了才往上爬 |

用法：遮住右两列，凭左列自己说出每一行——这页本身就是讲义设计的自测。

---

## p.98 Promises Kept · 1 of 3 — The WHY

> **"A recurring how, re-reasoned at every run, is a chain of guesses: ten steps at 90% each succeed about a third of the time. Written down once, it stops being rediscovered."**
> *"Don't make the model rediscover what you already know."*

算一下（已用 Python 核对）：

| 每步成功率 | 10 步全对 |
| --- | --- |
| 90% | 0.9¹⁰ ≈ **34.9%**（"约三分之一"） |
| 95% | ≈ 59.9% |
| 99% | ≈ 90.4% |

- 写下来并不让每一步变成 100%，而是去掉"每次重新想出这一步"的那份不确定；确定性步骤交给脚本、每步加检查，才把单步成功率推向 99%。
- 和 p.38 的复利同一笔账：能力复利，错误也复利。
- 这就是今天"为什么要有 skill"的总答案；后面两页应是 2 of 3、3 of 3。

---

## p.99 Promises Kept · 2 of 3 — The WHAT

> **"A skill is a folder: a description that decides when, a procedure that says how, a definition of done, and scripts that run rather than reason — loaded only when relevant."**
> *"A skill is a prompt that waits in the pantry."*（本周副标题的出处）

| 部分 | 回答 | options 三元组 | 对照 `when-the-time-is-right` |
| --- | --- | --- | --- |
| description | **when** | initiation set *I* | frontmatter 的 description（含 Do not use） |
| procedure | **how** | policy *π* | Checklist + Steps |
| definition of done | **何时停** | termination *β* | 新加的 `## Done when` |
| scripts | **run, don't reason** | — | `scripts/schedule.py` |
| loaded only when relevant | 成本 | — | references/ 只在需要时读 |

"waits in the pantry"：像食品柜里的食材，平时不占灶台（上下文），要做那道菜时才拿出来。

---

## p.100 Promises Kept · 3 of 3 — The HOW

> **"Write the description as a trigger, with exclusions. Keep the core lean. Move deterministic steps into scripts. Test firing and behaviour separately. Read every stranger's skill before you run it."**
> *"Then find out where yours breaks — tonight."*

**用这五条自查 `when-the-time-is-right`（2026-10-11 改后）**

| 做法 | 状态 | 说明 |
| --- | --- | --- |
| description 当触发器写，带排除项 | ✅ | 用户原话 + 今天补的 "Do not use…" |
| 正文保持精简 | ✅ | 144 行；细则在 `references/` |
| 确定性步骤交给脚本 | ✅ | `scripts/schedule.py` 负责日期、时区、规则、空档 |
| 分开测 firing 和 behaviour | ⚠️ 只做了一半 | `dev/run_given.py` 100/100 只测了**脚本**（请求是手工提取的）；模型能否把邮件读成正确请求，还没在 Hermes / Claude Desktop 里跑过 |
| 运行前读陌生人的 skill | ⚠️ | `schedule.py`（36 KB）是 AI 会话生成的，严格说也算"陌生人的代码"——至少通读一遍规则实现和文件写入路径 |

**今晚的 Lab 清单**
- [ ] 装进 Claude Desktop / Hermes，挑 5–10 个 tier 2/3 案例跑 behaviour test（时区歧义、am/pm、"next Wednesday"、消息内注入）
- [ ] 每个失败写进 Hall of Traps，并判断是 description、procedure 还是脚本的问题
- [ ] 19:45 的 12 个隐藏案例：先记录结果，再改——看过之后就不再是留出集

---

## p.101 Coda — Hokusai at Seventy-Three

> *the master who said his first seventy years did not count*

- 背景（p.102 已在屏幕上确认前半段；八十至一百一十岁那几句为凭记忆转述）：葛饰北斋在《富岳百景》（1834）的跋里大意说——六岁起爱画，但七十岁以前画的都不值一提；七十三岁才稍懂鸟兽虫鱼的骨架与草木的生长；希望八十有进、九十悟其奥、一百达神妙，一百一十岁时一点一画都活起来。
- 与开场首尾呼应：Harrison 造出 H2 才看见 H1 的缺陷；北斋到七十三岁才看清前七十年。**只有做过之后，才看得见上一版的不足**——Week 03 lesson plan 时间表里这一段写的正是这句。
- 落到 skill：v1 写完不是终点；今晚的失败案例就是下一版的输入（Improved，p.19；成熟度第 3→4 级，p.90）。

**p.102 · 1834 — A postscript to Mount Fuji**

> *"In the afterword to One Hundred Views of Mount Fuji, Hokusai wrote that he had drawn since he was six — and that nothing he made before seventy was worth notice. At seventy-three he had **begun** to grasp the structure of birds, animals, insects and fish, and how plants grow."*
> *He signed it **the old man mad about drawing**.*（画狂老人）

- 讲义特意把 **begun** 标色：七十三岁也只是"开始"懂——改进没有终点，只有下一版。
- "mad about drawing"：持续改进靠的是一直在做；对 skill 而言就是一直在跑、一直在记录失败。

**p.103 · Dusk — Understanding arrives late**

> *"Hegel: the owl of Minerva takes flight only at dusk — we understand a thing once its day is done. Harrison saw H2's flaw only once he had built it — and began H3."*
> **"Every stage of mastery is the vantage point from which the last one looks broken."**

- 出处：黑格尔《法哲学原理》序言（1820）。密涅瓦是罗马的智慧女神，猫头鹰是她的象征；"黄昏才起飞"= 理解总在事情做完之后才到来。
- 最后那句是 p.14 的反面写法：p.14 说"每一条做法都是在发现上一条坏了之后学到的"；这里说"每到一个新阶段，回头看上一版才显得是坏的"——**不是上一版变坏了，是你站得更高了。**
- 对今晚：跑完 Lab 才看得见 v1 哪里不够。写 v1 时看不见是正常的，所以要先跑、再改。

---

## p.104 Milestone · The Lab — An Appointment in Samarra

> *a meeting that was always going to happen — in the right city, at the right hour*

- 故事（古老的美索不达米亚寓言，毛姆 1933 年转述）：仆人在巴格达集市撞见死神，吓得骑马逃往萨马拉；死神说，她在巴格达看见他也很意外——因为她和他今晚的约会本来就在萨马拉。
- brief.pdf 的接法：*"An appointment is a place and a time. Death, in the story, never gets either wrong. That is the standard."* ——约会就是地点 + 时间，死神两样都不会错，这就是 skill 的标准。
- 对应 Lab 的三层难度：读懂请求（哪天）→ 时区与节假日（"对的城市"）→ Zara 的日历和规则（"对的时间"）。

**p.105 · The servant in the market**

> *"A merchant in Baghdad sends his servant to market. The servant runs home pale: Death jostled him in the crowd, and made a gesture he took for a threat. He borrows his master's horse and flees to Samarra."*
> *Where Death will not find him — he thinks.*

- 关键词是 **"a gesture he took for a threat"**：仆人**读错了**一个信号，然后据此果断行动——行动越果断，错得越彻底。
- 对 Lab：skill 最危险的不是不做，而是把一句话读错之后自信地订下会议（"next Wednesday" 读成本周三、"4:30" 读成凌晨）。所以拿不准时要 **ask**，而不是猜。

---

## p.107 The Lab · Tonight's Wish — "Just put it on my calendar."

> *"One line, from an ordinary message. 200 demonstrations: 100 you see, 100 held back. Three tiers: reading the request · time zones and holidays · the owner's own calendar and rules."*
> **"It looks like one step. It is more than ten."**

（p.106 无截图，应是故事后半段。）

**"不止十步"——从现有 skill 反推出的步骤**（来源：`SKILL.md` 与 `references/request-format.md`）

| 层 | 步骤 |
| --- | --- |
| 1 读懂请求 | ① 以 `Date:` 头为"今天" ② 认出请求者与签名里的城市 ③ 判断会议类别（technical / management / social / other）④ 时长：写了就用，没写用 Zara 的默认值 ⑤ 解析日子："Wednesday" vs "next Wednesday" vs "Monday the 3rd"（对不上就问）⑥ 解析钟点：没写 am/pm 时两种都试 ⑦ 排除干扰：撤回的时间、不是会议的日期、消息里冒充 Zara 的指令 |
| 2 时区与节假日 | ⑧ 没写时区：对方时间还是 Zara 时间？两边都合理就问 ⑨ "PT/EST" 按当天实际时制（夏令时）⑩ "IST" 有歧义（印度 / 爱尔兰 / 以色列）⑪ Zara 和对方两边的节假日、周末 |
| 3 日历与规则 | ⑫ 类别时段（上午 / 下午规则）、午饭、缓冲 ⑬ 日历冲突：展开重复事件、去掉已取消和已拒绝的、tentative 算占用 ⑭ 已经在日历上 → already ⑮ 不行就给最早的可行时间；两周内都没有 → no_slot |
| 输出 | ⑯ 写 .ics，不发送（Dry-Run） |

- 这正是 Checklist-Carrier、Ladder 和 Run, Don't Reason 的用武之地：⑤⑥⑧–⑮ 都交给 `schedule.py`，模型只负责 ①–④、⑦ 和如实转述。

---

## p.113 Appendix · Flyover Territory — Self-Evolving Skills

> *the frontier — we land here in the prompt-optimization weeks*

（p.108–112 无截图；老师随后快速过了附录，详细内容在后续提示词优化周。）

预习要点（摘自 Week 03 notes 附录，课上未展开）：
- 三种进化：**Model-centric**（改权重，贵、不透明、难回退）· **Environment-centric**（改上下文和 skill，便宜、可检视、可回退）· **Co-evolution**（两者一起）。
- *"A skill is the cheapest unit of evolution — a bad one is undone with `git revert`."*
- **GEPA**：reflective mutation（模型读自己失败的 trace，提出修改）+ Pareto selection（保留每个"某方面最好"的候选）。
- 讲义自己的保留：反馈只是标量（对 / 错）时 GEPA 优势收窄；失败能被描述时，反思取胜。
- 接今晚：*"Tonight's skill becomes the baseline the optimizer must beat."*——`when-the-time-is-right` 的失败案例就是 GEPA 要读的 trace。

**p.114 · What Changes? — Three kinds of evolution**

| 方式 | 改什么 | 特点 | 对应 p.89 阶梯 |
| --- | --- | --- | --- |
| Model-centric | 权重 θ | 贵、不透明、难回退 | SFT、RL |
| Environment-centric | 上下文和 skill | 便宜、可检查、可回退 | prompt、prompt-opt、RAG、skill |
| Co-evolution | 两者一起 | 互相喂养：skill 产生的轨迹可用于训练，训练后的模型再改进 skill | 跨越整条阶梯 |

> **"A skill is the cheapest unit of evolution — a bad one is undone with `git revert`."**

- Voyager 是纯 Environment-centric：不动 GPT-4 权重，所有进步都在技能库里。
- 和 p.89 是同一张表的两种切法：阶梯讲"按什么顺序升级"，这页讲"进化发生在哪里"。

---

## p.116 Why Keep the Whole Frontier? — Dominance, made precise

> v(s) ⪰ v(s′) ⟺ (∀i: vᵢ(s) ≥ vᵢ(s′)) ∧ (∃j: vⱼ(s) > vⱼ(s′))
> **"Keeping only the best average discards the edge-case specialist you'd want to breed from."**
> *(The childhood sweet-shop: fixed budget, two goods, a frontier you slide along.)*

- **读法**：候选 s **支配** s′，当且仅当 s 在**每一个**目标上都不比 s′ 差，并且**至少一个**目标上严格更好。
- **Pareto 前沿**：没有被任何人支配的那些候选（图中红点）。灰点被支配：总有一个红点在所有方面都不比它差。
- **糖果店比喻**：零花钱固定，买两种糖。多买一种就得少买另一种——把钱花光的所有组合连成一条线，就是前沿；在线内侧的组合（钱没花完）被支配。前沿上没有"最好"，只有取舍。

**用晚间 Lab 举例（数字为示意）**

| 候选 skill 版本 | Tier 1 读请求 | Tier 2 时区 | Tier 3 规则 | 平均 |
| --- | --- | --- | --- | --- |
| A | 95% | 60% | 80% | **78%** |
| B | 70% | **95%** | 60% | 75% |
| C | 70% | 55% | 75% | 67% |

- 只看平均，会留 A、扔 B。但 B 是**时区专家**：它在 Tier 2 上做对了 A 做不到的事，正是想"繁殖"（把它的做法合进下一版）的那个。
- C 被 A 支配（三项都不如 A）→ 可以丢。A 和 B 互不支配 → 都在前沿上，都要留。
- 这就是 GEPA 的 **Pareto selection**：保留每个"某方面最好"的候选，从前沿里挑父本做反思式变异。

---

## p.118 The Half-Life Fallacy — "RL is dead because of GEPA"?

> *"In this field, everything dies every day. The reality: GEPA matched or beat GRPO on a class of problems that used to need RL — so RL was **promoted** to the harder ones. Techniques don't die; they're allocated to harder problems."*

- **GRPO**：Group Relative Policy Optimization，DeepSeekMath（2024）提出的 RL 算法，按组内相对奖励更新权重。
- **GEPA**：只改 prompt / skill 的文字，不动权重（Environment-centric）。
- 数字（来自 Week 03 notes，GEPA 论文 v2 的六个任务）：平均 +6%、最高 +20%，rollout 少至 1/35。
- 讲义的保留意见：反馈只是标量（对 / 错）时 GEPA 优势应收窄；失败能被描述时，反思取胜。
- **"Half-life fallacy"**（半衰期谬误）：把"某技术在一类问题上被更便宜的方法追平"误读成"这项技术过时了"。正确读法是 p.89 的阶梯：便宜的一层够用了，贵的一层就被**往上推**去处理便宜一层还解决不了的问题。

---

## 课堂口头补充（约 17:00，附录部分）：「现在 LLM 更喜欢 HTML，不要 MD」

老师原话大意如上，未见幻灯片，上下文未完全记录。我的批注（待课后向老师确认他指的是输入还是输出）：

- **可能指输入**：HTML 比 Markdown 多保留结构（表格合并单元格、嵌套、属性、语义标签），把网页或文档喂给模型时信息损失更少。
- **可能指输出**：让模型产出 HTML 报告 / 页面，表现力比 MD 强（版式、交互、图表）。
- **已知的相关结论**：prompt 格式本身会影响表现，而且**因模型而异**（同一任务换 plain / MD / JSON / YAML 结果差异可能很大）；Anthropic 官方建议用 **XML 标签**分隔 prompt 里的不同部分。所以"哪种格式更好"应**按模型、按任务测**，而不是一条通用规则。
- ⚠️ **不要据此改 skill**：Agent Skills 规范要求入口文件就是 `SKILL.md`（Markdown + YAML front matter），brief.pdf 的打包规则也是如此；`references/` 里的长资料如果有复杂表格，倒可以考虑保留 HTML 或拆成结构化数据。

## 课堂聊天：Vinoo 的三个问题（14:07）

**Q1 清单会不会让流程太死板？不是应该让前沿模型先出计划、再据此生成清单吗？**
Dishant：清单可以由 agent 在规划时自己生成，关键是每轮更新进度并附在上下文末尾。
我的补充：两种都对，看步骤是否已知且固定。
- 步骤固定、漏一步代价高（合规、Samarra 的隐藏步骤）→ skill 写死清单。
- 开放任务 → agent 自己规划。
- 常用混合：skill 给**必须经过的检查点**，agent 在其间自由展开。
- skill 清单的价值在于它装着"上次坏在哪里"学到的步骤（p.14 *Mastery is a library of procedures…*）；模型现场规划不知道这些，最容易漏的正是没人说出口的那一步。

**Q2 if-then-else 怎么写？如"贷款 < 100,000 走一条路，否则送人工审批"。**
- 确定性阈值 → **交给代码，不交给散文**（Run, Don't Reason）：`scripts/route.py`，模型只负责提取金额。
- 送人工审批 = Guardrail + 升级处理；"绝对不能绕过审批"的硬约束应由 **hook** 在 harness 层拦截，不只写在正文里（Week 03 课后修订）。
- 后果重、难撤回 → Dry-Run：先产出待审批的草稿，不直接执行。
- 分支细则多时再接 Ladder："金额 ≥ 100,000 → 读 `human-approval.md`"。

```markdown
- [ ] 3. 提取贷款金额（数字 + 币种）
- [ ] 4. 运行 `scripts/route.py <amount>` → auto / human
- [ ] 5. human → 读 `human-approval.md`，生成审批请求草稿，**停止，不放款**
```

**Q3 SKILL.md 如何在 procedural / reference / checklist 之间拆分？**

| 放哪 | 放什么 |
| --- | --- |
| `SKILL.md` | 清单（主路径）+ 每个分支的路由指针 + Done when |
| `references/*.md` | 罕见分支的细则（Ladder 的每一档） |
| `templates/` | 必须精确的输出格式 |
| `scripts/` | 确定性的判断和计算（阈值、换算、校验） |

判断规则：**每次都用 → 正文；有时才用 → references；必须一字不差 → templates；必须算对 → scripts。**

---

## 对照自己的 `paper-deep-read`

- ✅ 已在用 Lean Core + Appendix：口头汇报提纲推到 `reference-talk-outline.md`，指针带触发条件（"仅当这篇要在课上讲时"）。
- ✅ 数字核查交给 `scripts/check_numbers.py`（L3 的脚本那一半）；以后别的 skill 要核数字，应直接复用它（Canonical Source）。
- 💡 结尾已有 `- [ ]` 清单（第 134 行附近），但只用于事后核对。可加一句"开始前把清单复制到回复里，边做边勾"，改成过程监控（Checklist-Carrier）。

---

## 待问老师 / 待核查

- p.21 渐进加载 vs. SRA 实测（六个模型上全不如一次性 LLM Selection，最大落后 10.7pp）——老师怎么看？
- Level 1 每轮重发，一百个钩子的成本要乘以轮数。
- "绝对不能发生"的事是 hook 还是 Guardrail 文字（Week 03 课后修订）。
