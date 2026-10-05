# Week 03 第二场 · Agent Skills 田野调查

> 课堂第二份 deck（文件名 `skills-field-survey-with…`）+ 一份《Inside the harness》邻居图 + 一份参考资料 deck。
> **主讲另有其人**（Raju Godavarthy 在场，Asif 操作）；本文按我截到的页整理。
> 整理于 2026-10-05 · 日期和数字照抄屏幕，**未逐条打开原始来源核对**

> ⭐ 这场和主讲 Skillcraft 的分工：**Skillcraft 讲应该怎么做，这场讲市场上实际是怎么做的——而两者不一致的地方最有价值。**

---

## 〇 · Inside the harness：每个邻居住在哪

> 名称按 Claude Code · **红色 = 由 harness 加载或强制执行**

### 上下文窗口里有什么，按顺序

| | 什么时候进来 |
| --- | --- |
| *system prompt 区* | |
| `CLAUDE.md / AGENTS.md` | **每一轮** |
| Scoped rules | **路径匹配时** |
| 🔴 **Skill list · Level 1** | **每一轮** |
| *messages 区* | |
| User message | |
| 🔴 **Skill body · Level 2** | **被选中或 `/名字` 时** |
| Subagent summary | 追加 |
| Tool results | 追加 |

### 循环

```
User → [context] → Model → 🔴 Hooks → Tools → MCP servers
                     ↓      allow / block
                  Subagent
                  自己的 context 和 model 调用
                  只有 summary 回来
                     ↓
              结果追加回 context
```

**Plugin**：*installs skills, subagents, hooks and MCP config as one bundle.*

### ⭐ Sandbox 为什么不在这张图里

**因为这张图画的是信息流（什么进上下文），而 sandbox 管的是执行权限——两个正交维度。**

**Sandbox 不是流程里的一个盒子，是 `Tools` 那一格的运行环境：**

```
Model → Hooks → Tools → MCP servers
                └─────┘
                这一段在什么环境里执行 ← sandbox 包的是这里
```

| 场景 | 脚本在哪跑 | sandbox |
| --- | --- | --- |
| **Hermes** | 你的机器，它启动的那个终端 | ❌ **用你的权限** |
| **Claude Desktop** | **Claude 自己的 sandbox** | ✅ 你的文件不可见、常常无网络 |
| Claude Code | 你的机器 | ❌（有权限提示，但不是隔离） |
| Kitchen 的 Bazaar tab | app 模拟的"厨房" | ✅ 可开关 |
| 生产部署 | 你自己建的容器 | 看你怎么建 |

⚠️ **Agent Skills 规范只约束 `name` 和 `description`——跑在哪、有没有隔离，完全由客户端决定。** 这正是作业第 1 条要验的东西。

**它干什么：拿掉出路。** Bazaar 那个实验问得最准——*"when the sandbox was on, what had changed — the model, or the kitchen?"* **答案是厨房。**

```
私有数据  +  不可信内容  +  对外通信
              ↑              ↑
          审计攻击这条    sandbox 拿掉这条
```

🔑 **三条腿缺一条就不成立。而审计靠"你没看漏"，sandbox 不靠任何人的判断力。**

### ⭐⭐ Hooks vs Sandbox：三级硬度

| | Hooks | Sandbox |
| --- | --- | --- |
| 挡在哪 | **调用之前**，按你的规则 allow / block | **执行环境**上，物理上做不到 |
| 是什么 | **策略** | **能力边界** |
| 能被绕过吗 | **能**——如果规则有洞 | **不能**——它不是规则，是缺失的能力 |

```
Hook：   「禁止调用 curl」        →  模型改用 python requests 就绕过了
Sandbox：容器里根本没有网络接口   →  用什么都没用
```

🔑 **所以「绝对不能发生的事该是 hook」还可以再精确一级：**

```
"应该拒绝"（有例外）        →  skill 里的 Guardrail 文字
"绝不允许"（能列举得完）     →  hook
"连做都做不到"              →  sandbox / 权限
```

**三级，一级比一级硬。** 讲义 p.62 那句也在这条线上：*"A Level 3 script is a privilege: **least privilege · sandbox · read before you run**"* —— **三个动作分属三级。**

### 四样讲义没讲的

**① Hooks —— 闸门的实物。** 红色，坐在 Model 和 Tools 之间，`code: allow or block`。七个动词里 *enforces* 的落地点，也是做权限、预算、Dry-Run 确认的地方。

**② Scoped rules —— 持久性光谱比四层更细。**

```
CLAUDE.md      每轮都在        ≈ system prompt
Scoped rules   路径匹配时才进   ← 由 harness 按规则判断，不走模型
Skill L1       每轮都在
Skill L2       被选中时
```

🔑 **"when paths match" 是一种不靠模型判断的条件加载**——比 skill 的语义触发便宜也确定得多。

**③ Subagent —— *"only a summary comes back"*。** 子 agent 有自己的 context 和 model 调用，**烧掉的 token 不进父上下文**。
🔑 **这是压 `κ` 的强力手段**：让子 agent 读十万字，父上下文只付那三句摘要的钱。也回答了听众那个"Can sub-agents have a skill?"——能，而且**子 agent 加载的正文不占父上下文**。

**④ 布局细节：L1 在 system prompt 区，L2 在 messages 区。**

```
L1 → 每一轮重新发送          ← 一百个钩子要乘以轮数
L2 → 追加一次，之后作为历史    ← 只付一次
```

**讲义说 L1「约一百 token」听起来很少，但那是每轮的单价。**

---

## 一 · 市场图景

### 1.1 Skills 爆发了，而市场大部分是噪声

| | |
| --- | --- |
| **31,132** | 两个公开市场的独特 skill，**2025-12**（Liu et al., `arXiv:2601.10338`） |
| **11,497** | 四个市场的软件工程类 skill，**2026-06**（Cao et al., `arXiv:2607.09065` = *Inside the Skill Market*） |
| **46%** | 市场 skill **与至少一个其他 skill 重名**（Firecrawl 报告，**2026-02**） |

> **丰饶先于策展而至。一次重名就是 ACT V 的 Collision 坏味道，放大到整个市场的尺度。**
> **类比：** 一个开张第一年的应用商店——**数量很唬人，搜索结果不行。**

⚠️ **三个数字的证据等级不同：** 前两个是 arXiv 论文，第三个是**厂商博客**。
⚠️ **46% 是冲突的下界。** 重名只是最容易自动测的那种；**描述语义重叠而名字不同**的冲突爬虫测不出来，而且更常见。

↔ 和 Snyk 的 **36.8% 有安全缺陷**放在一起：**市场既不安全，又分不清。**

### 1.2 两套正交的分类

> 眉题自带免责：*"A working taxonomy for this session, **not an official standard**."*

| **它携带什么**（形态） | | **它干什么活**（用途） | |
| --- | --- | --- | --- |
| Prose only | 一门手艺，用文字写 | File formats | docx, pptx, xlsx, pdf |
| Reference pack | 按需读的参考页 | Engineering method | TDD、调试、评审 |
| Script-backed | 会跑但不被读的代码 | **Vendor onboarding** | 正确使用我们的 SDK |
| Template-bearing | 输出的精确形状 | Tool companion | 覆盖在 MCP 访问之上的判断 |
| Orchestrator | 一串其他 skill | Domain playbook | 一个分析师的方法 |
| **Meta-skill** | **造 skill 的 skill** | **Taste and brand** | **什么才算好** |
| | | Security review | 一个审计师的方法 |
| | | Personal and team | 我们做事的方式 |

**两个轴正交**——一个 skill 同时有形态和用途。

左列基本是 deck p.70 structural patterns 的改名；**Meta-skill 是新的**（`skill-creator` 就是）。
右列三个值得单独记：**Vendor onboarding**（商业模式）· **Taste and brand**（g 最难测但最值钱）· **Tool companion**（= Skill + MCP）。

---

## 二 · skill 里装什么

### 🔥 三分之二的 skill 只是文字

**11,497 个 SE skill 的结构构成**（Cao et al., 2026）：

| | |
| --- | --- |
| Instructions only | **63.8%** |
| Documentation | **18.6%** |
| **Scripts** | **10.5%** |
| Agent workflow | **3.9%** |
| Library | **2.0%** |
| Application | **1.1%** |

> **只有十分之一带脚本。** 大多数作者把流程编码成文字然后相信模型会照做。**这写起来便宜、读起来容易。** 但也意味着**绝大多数已发布的 skill 把算术、日期和格式又塞回了模型手里——这正是 Run, Don't Reason 的反面。**

⚠️ **别读过头：63.8% 不等于 63.8% 的作者偷懒。** 很多 skill 本来就只有判断没有计算（Taste and brand 那类配什么脚本？）。**这是个上界提示，不是结论。**

🔑 **一个 deck 没说的推论：带脚本的 skill 不只更准，还更便宜。**

```
纯文字 →  整个正文进上下文  →  κ 全额
脚本型 →  代码不进上下文    →  那部分 κ = 0，只有输出的几十 token
```

**Script-backed 把加载规则的两边同时往好处推。** 而 63.8% 那根最长的柱子，两边都付全价。

---

## 三 · skill 干什么用

### 3.1 🔥 skill 堆在写代码周围，需求几乎没人写

**生命周期阶段分布**（同一份 11,497）：

| | |
| --- | --- |
| Implementation | **25.0%** |
| Testing | **21.3%** |
| Code review | **19.1%** |
| Plan and design | **13.1%** |
| Maintenance and ops | **10.8%** |
| Deployment | **5.3%** |
| Release | **3.2%** |
| **Requirements** | **2.2%** |

三个最常见活动约 **2,900 / 2,300 / 2,000** 个 skill（代码评审、测试自动化、安全审计）。

> **那些最依赖上下文的阶段——客户到底是什么意思、这个版本为什么是这个形状——恰恰是最少被写下来的。而那正是一个团队自己的 skill 最值钱的地方。**

⚠️ **我的修正：2.2% 可能是采样偏差，不是需求缺口。** 这是**公开市场**的数据，而 requirements 类 skill 天然是内部的——"我们客户说'尽快'的意思是两周"没人会发到市场上。**但这反而加强了结论：市场不会供给，你只能自己写。**

🔑 **而且这和 `g` 正好反着来：**

```
通用 skill（code review 的一般规则）  模型本来就会七八成  →  g 小
团队特定（我们怎么判断需求清晰）      模型完全不知道      →  g 大
```

**g 最大的地方，正是市场最空的地方。** 从市场装一百个 skill，装到的大多是 g 小的那类——**数量上去了，能力没上去多少，而每一个都在收 κ。**

### 3.2 厂商现在把 skill 和 SDK 一起发

来源：VoltAgent/awesome-agent-skills，**2026-10**

| | |
| --- | --- |
| **Sentry** | 跨 **30+** 平台的 SDK 配置 |
| **Stripe** | 集成最佳实践、SDK 升级 |
| **Cloudflare** | Workers、Durable Objects、KV |
| **Vercel** | Next.js 最佳实践、升级 |
| **Supabase** | Postgres 最佳实践 |
| **Hugging Face** | datasets、TRL 训练、评测 |
| **HashiCorp** | Terraform providers 和 modules |
| **Microsoft** | **133 个 Azure skill，五种语言** |

> **这是写给一类新读者的文档：一个会替开发者配好 SDK 的 agent——而那个开发者从不打开文档。**
> **类比：** 厂商经过验证的设计指南，**装在盒子里一起发，而不是挂在一个没人访问的门户上。**

🔑 **为什么这类会爆发（和 3.1 正好反着）：** 它是唯一同时满足两头的——**既通用**（所有用 Stripe 的人）**又高 g**（模型确实不知道 SDK 上个月改了什么）。

⚠️ **两个 deck 没提的风险：**

**① 商业倾向。** vendor skill 是**带商业动机的文本**，而它会直接进入上下文影响决策。"integration best practices" 里推荐的，可能恰好是利润更高的那个产品。**这不是恶意，是倾向——而倾向比恶意更难审**（审计查得出密钥外传，查不出"这个建议对谁更有利"）。按**有利益相关方的文档**读，不是中立参考。

**② 133 个全装上 = 每轮多付约 13,300 token。** 答案不是都装——按项目装，或者上 embedding 检索。

**③ Stale 风险在这类上最高。** SDK 升了 skill 没跟上 → **模型会自信地用旧 API，而且你不会立刻发现。** 装 vendor skill 要跟着 SDK 版本一起钉。

### 3.3 领域 playbook 打包的是方法，不是数据

六个金融 skill（Anthropic, Claude for Financial Services, 2025-10-27）：Comparable company analysis · Discounted cash flow · Due diligence data packs · Company teasers and profiles · Earnings analyses · Initiating coverage reports

> **事实来自数据源和检索；skill 说的是拿这些事实做什么。**

> 🏢 **Rakuten 出现在这页上：** *"Rakuten reported finance reporting work falling from a full day to about an hour."*（Rakuten via Anthropic, **2025-10-16**）
> ⚠️ 这是**经厂商发布的自报数字**，和 Cao et al. 那种论文统计不是一个证据等级。

🔑 **为什么这条边界非划不可——三个理由：**

1. **数据会过期，方法不会。** 把本季度的 WACC 写进正文 = 保证 Stale。
2. ⭐ **数据有权限，方法通常没有。** `方法 → 全公司共享一份；数据 → 按用户隔离`。**一旦正文里装了数据，它就不能共享了**，你得给每个团队分叉然后看它们漂移。
3. **g 在方法这一侧。** DCF 的数学模型会算，**你们怎么设假设它不知道**。

### 3.4 ⭐ 把你的 runbook 变成一个 skill（十三行，四个模式）

```yaml
---
name: incident-triage
description: Triages a new production alert
  for the payments service. Use when an
  alert or page is pasted in. Do NOT use
  for post-incident reviews.
---
1. Classify severity: references/sev.md
2. Pull the last deploy and error rate
   (MCP: observability)
3. Propose a rollback; wait for a human.
## Done when
Severity set, owner paged, timeline
started in the incident doc.
```

| 行 | 在做什么 |
| --- | --- |
| `for the payments service` | **限定了服务**，不是所有告警 |
| `when an alert or page is pasted in` | **用户的真实动作**，不是术语 |
| `Do NOT use for post-incident reviews` | 排除项，挡的恰是**最容易混的邻居** → **Pushy Trigger with exclusion** |
| `references/sev.md` | 严重度矩阵不进正文 → **Lean Core + Appendix** |
| `(MCP: observability)` | **Skill + MCP** |
| `Propose… wait for a human` | **Dry-Run + escalate**：回滚不可逆，skill 只到"提议"为止 |

⭐ **最该学的是 Done when：`Severity set, owner paged, timeline started`——三个可以去查的二值事实。** 比"处理完了"强，也比"rinse water runs clear"这种观察更强，因为**两个人核对会得到同样的结论**。

**"Where these come from"：** Runbooks · onboarding checklists · month-end closes · report formats
🔑 **四个共同点：反复做、步骤固定、团队特有、现在只活在某个人脑子里或一份没人看的文档里。** 结合 3.1 的 2.2%——**这四类正是市场永远不会给你的。**

---

## 四 · 怎么写（五段工作流）

### 4.1 先确认它该不该是 skill

| 如果是…… | 那就该是…… |
| --- | --- |
| 一次性的请求 | **just a prompt** |
| 几乎每轮都需要 | **system prompt 或 AGENTS.md** |
| 会变的事实（价格、政策） | **retrieval** |
| **绝对不能发生的事** | **🔴 a hook or a permission** |
| 访问另一个系统 | **an MCP server or a tool** |
| **反复、多步、有时候需要** | **a skill** |

🔥 **第四行是对主讲的一处修正。** Deck p.71 把 **Guardrail** 列为 skill 的行为模式；**这里说如果是"绝对不能发生"，它就不该待在 skill 里。**

```
skill 里的 guardrail  =  模型【读到】然后【选择】遵守的文字
hook / permission     =  代码【强制】执行，模型同不同意不相干
```

**正文会被别的指令挤掉、被长上下文稀释、被更强的措辞覆盖；hook 不会，因为它根本不经过模型。**

| | 用什么 |
| --- | --- |
| "应该拒绝"（有例外的判断题） | skill 里的 Guardrail 模式 |
| **"绝不允许"**（没有例外） | **hook / 权限** |

🔑 这也回答了听众那个 **"Skill verifier or validator?"**——**validator 是 hook，verifier 可以在 skill 里。**

### 4.2 挑一件模型没法一步做完的事

| **太简单 · 很少触发** | **值得做成 skill** |
| --- | --- |
| `"Read this PDF."` | `"Fill the vendor W-9 in this PDF from our supplier sheet, and flag anything missing."` |
| `"Convert 3pm PT to London."` | `"Put this on Zara's calendar."` |
| `"Summarize this email."` | `"Draft this week's status update in our team format."` |

> **Agent 只在自己不容易搞定的任务上才去查 skill。一个完美的描述，也不会让它在一个单步请求上触发。**

🔥 **这比"g 小不划算"更硬——是机制层面：它压根不会触发。**

```
经济学说法：  p 高 × g 小 − κ  →  VoL 为负  →  不该加载
实际机制：    模型能一步做完    →  不会去查  →  p 本身就塌了
```

**"写得更 pushy 就能救"这条路被这句话堵死了。**

🔑 **右列每条都藏着一个模型不知道的本地上下文：** `our supplier sheet` / `Zara's calendar` / `our team format`。**"our" 就是 g 的来源。**

### 4.3 动笔前回答四个问题

| | |
| --- | --- |
| **它让 agent 做什么？** | 一句话一件事。**如果你需要两个 "and"，那可能是两个 skill。** |
| **何时触发？** | 真实用户会敲的说法，**以及它必须保持安静的那些近似情况**。 |
| **输出长什么样？** | 一个文件、一个格式、一条消息、一个动作。**找一个或做一个完美样例。** |
| **你怎么知道它成功了？** | **两三个真实的测试提示词，以及一个好结果里包含什么。** |

### 4.4 建一个 skill 是一个循环，不是一份文档

```
Scope → Draft → Test → Review → Improve
         ↑_______________________|
    repeat until the reviews come back empty
```

| 格 | 原文细节 |
| --- | --- |
| Scope | what it does, when it fires, what done looks like |
| Draft | a lean SKILL.md and the scripts it needs |
| **Test** | **realistic prompts, with and without the skill** ← **这就是测 `g`** |
| **Review** | outputs and transcripts, **by a person** ← 不是让另一个 agent 评 |
| Improve | generalize the fix; cut what doesn't help |

> 然后加宽测试集、调触发词、打包。**第一版草稿是这件事里最便宜的部分。**

🔑 **终止条件是 *"until the reviews come back empty"* —— 不是"写完了"，是"挑不出毛病了"。**

### 4.5 用祈使句写，并把理由附上

| **RIGID** | **EXPLAINED** |
| --- | --- |
| `ALWAYS attach the receipt.`<br>`NEVER submit over $75 without approval.`<br>`YOU MUST use the template.` | **把收据图附到每一行；** 财务会退回没有收据的行。<br>**超过 $75 的先走经理；** 那是审批额度，而且晚审批会拖慢所有人的发薪。 |

> **Anthropic 自己的指南把全大写的 ALWAYS 和 NEVER 列为黄旗。一个知道为什么的模型，能处理你没列出来的那种情况。**

🔑 **理由是泛化的载体。** `NEVER submit over $75` 答不了"正好 75 呢""拆成两笔呢"；**但知道"那是审批额度，绕过它会拖慢所有人"，拆单它自己就识别出来了。**

↔ **带理由的指令能抵抗规格博弈**——博弈博的是字面，理由给的是意图。

**实用测试：** 写下 ALWAYS/NEVER 之前先试着说出理由。**说不出 → 这条规则你自己也没想清楚；说得出 → 写上理由，吼就不必要了。** 而真正不能有例外的，按 4.1 那条，**该是 hook 不是文字。**

### 4.6 展示一个好的输出样例

```
## Commit message format
Example:
  Input:  Added login with JWT tokens
  Output: feat(auth): implement JWT-based login
```

> **一个样例胜过一页规则。** 模型会复制它的形状。
> **但这把刀两面开刃。** Agent 把样例当作**可信的参考代码**来抄，**这正是被投毒的样例发动攻击的方式**。样例要**小、正确、而且是你自己的**。
> **需要精确版式的，在 `assets/` 里带一个模板。**

⚠️ **这是第三个攻击面。** Deck p.55 只说两个（prose that steers / scripts that run）；**examples that get copied 既不是指令性散文也不是会执行的脚本，两个审查视角都可能漏掉。**

**四个目录四种用途：**

```
SKILL.md       ← 小样例放这儿，展示形状
references/    ← 大的参照文档
assets/        ← 精确模板，要原样套用的   ← Template-Bearer 的落点
scripts/       ← 跑而不读
```

### 4.7 写能在任何地方跑起来的脚本

| | |
| --- | --- |
| **标准库优先** | agent 通常不会替你装包。真要用，**在 description 的兼容性说明里写出来** |
| **路径从 skill 文件夹算起** | **"当前目录"在不同 agent 里不一样** |
| **两个文件夹分开** | **skill 文件夹只读**；输出写到工作目录 |
| **检查解释器** | 版本太老就停下，**给一条人能据此行动的消息** |
| **默认没有网络** | 有些 agent 在无网 sandbox 里跑 |
| 🔥 **别遮蔽标准库** | **`calendar.py` 会把 Python 的 `calendar` 模块藏起来** |

> ⚠️ **最后一条今晚会咬人。** 日历 lab 里最顺手的三个名字 `calendar.py` / `time.py` / `datetime.py` **全是地雷**，而且症状极难查——抽屉里的 `convert_time.py` 内部多半 `import datetime`，你放一个同名文件，**别人的脚本会先 import 到你那个**。
>
> 讲义给的四个脚本名全避开了：`convert_time.py` / `find_holidays.py` / `count_business_days.py` / `write_invite.py`——**全是动宾结构。** *"Name files for what they do."*

**第四条的措辞值得学：** *"stop with **a message a person can act on**."*

```
❌ ImportError: cannot import name 'UTC' from 'datetime'
✅ 需要 Python 3.11+，当前 3.9。试试：uv run --python 3.12 python <script>
```

### 4.8 ⭐⭐ 修原则，不是修测试用例

| **过拟合的补丁** | **通用的修法** |
| --- | --- |
| `If the message says "next Friday" and was sent on a Monday, use the date 11 days later.` | **"Next Friday" 本身有歧义。** 用主人 profile 里**写明的解读方式**，并且**在报告里永远显示完整日期，这样读错了几秒内就能发现。** |

> **你的测试集只是一把例子。这个 skill 会遇到成千上万个不在上面的请求。**

右边那段做了三件事，**第三件最聪明**：

1. **先承认歧义**，而不是替它挑一个答案
2. **把裁决权交给规格**（去读 profile），不是交给猜测
3. ⭐ **不保证读对，而是让读错立刻可见**

🔑 **这是一条 verifier 设计原则：当你无法保证正确时，让错误变得显眼。**

```
"Answer: 496"                           ← 差一天，完全可信，不会去查
"2021-12-01，共 497 天，起算 2020-07-22"  ← 差一天立刻有人看出来
```

**把中间结论暴露出来，是对抗"自信地错"的通用手段**——和 Dry-Run 同一个思路。

**实操判据：** 每次要改 skill 时问一句——**我是在写一条规则，还是在写一个 if？** 出现具体案例编号、具体日期、具体天数的，基本都是补丁。

---

## 五 · 听众问题清单（屏幕上的那份）

```
First current state
    Different reasons for Skills becoming the way …

Questions from the audience …
    is a Agent Skill is not a skill ?
    Is Skill mandatory in good Agentic system
        p(being valuable) > dilution
    Can Sub Agents have a Skill ?
    How do we handle Large number of Skills
    Skill verifier or validator ?
    Practical or team co-ordination problems in writing skills
    Testing Skills independently via CICD ?
```

| 问题 | 我的答案 |
| --- | --- |
| `p(being valuable) > dilution` | **就是加载规则**，只是省掉了 `g`。严格形式 `p·g > κ`，而 g 在分母里——**用处大的 skill 门槛自动更低** |
| Can sub-agents have a skill? | 能。deck p.72 的 **Skill-of-Skills** 和 **Subagent-backed**。硬条件：`β_A ⟸ β_B ∧ β_C ∧ A 自己的检查`——**子 skill 少一个 Done when，父流程的终止就不成立**。而且子 agent 的正文**不占父上下文** |
| 大量 skill 怎么办 | 小库全放上下文让模型选；大库先 embedding 检索。**但 SRA 实测 26,262 条上模型不会挑**（见下） |
| Skill verifier or validator? | **validator 是 hook（强制），verifier 可以在 skill 里（建议）**。Forge 把这两件事分得很干净：**✗ 格式错误该 fail build，○ 手艺建议只该 warn** |
| CI 里独立测 skill？ | 分两类：**firing test**（Fβ，漏触发更贵时 β>1）和 **behaviour test**（rubric）。关键是 *"agent B, **with no memory of the authoring**, tests"*——**CI 里必须是全新会话**。格式校验可用 `skills-ref validate`；行为测试没有现成工具 |
| 团队协作问题 | **最现实也最没有标准答案。** deck 只给了 Single Canonical Source 一条；**多团队共写一个库的版本管理没有覆盖** |
| Skill 是必需的吗 | **不是。** 按升级阶梯，g 不够大就不该做成 skill |

---

## 六 · ⚠️ 这场和主讲冲突的地方（最该记的部分）

| 主讲 Skillcraft 说 | 这场 / 论文的实测 |
| --- | --- |
| Guardrail 是 skill 的行为模式 | **"绝不允许"该是 hook，不是文字** |
| 确定性步骤交给脚本 | **市场上 89.5% 没有脚本**——这是最佳实践，不是现状 |
| 两个攻击面：散文 + 脚本 | **第三个：被复制的样例** |
| 渐进披露是 "the load-bearing idea" | **SRA 实测：六个模型上全不如一次性 LLM Selection**，最大落后 10.7pp |
| `VoL = p·g − κ` | **SRA 实测 need-awareness Δ = +0.1pp——模型基本不看 g** |
| "a rich repertoire is a durable enabler"（p.43） | **SkillsBench：2–3 个 skill 胜过 4+ 个；自生成 skill −1.3 分** |

### 🔑 "rich" 这个词指的是两种不同的东西

| Voyager 的 rich | 市场的 rich |
| --- | --- |
| **自己造的** | 别人写的 |
| **每条都过了自验证才保留** | 36.8% 有缺陷、46% 重名 |
| **单一任务域** | 跨领域大杂烩 |
| 规模未公布 | **26,262 ～ 一百万** |

**Voyager 证明的是"自己造、经过验证、同域"的库有用。** 它没有证明"从市场装三万条"有用。

而 SkillsBench 的 **+16.2（精选）vs −1.3（自生成）** 说得更直白：**差别不在数量，在策展。**

↔ Voyager 自己的 Table 1 早就有信号：**去掉技能库在石器级反而更快（9±4 vs 11±2）**，优势只在铁和钻石出现——**技能库有一个任务复杂度的启动门槛。**

### 🔥 "种子发芽了，但果是负的"

主讲 p.46 讲 Reflexion/ExpeL，收在"**一个 skill 改写自己正文的种子**"。

**三年后 SkillsBench 测了这颗种子：自生成 skill −1.3 分。**

这不否定 Reflexion 的机制（它测的是单任务内的反思重试，不是生成可复用 skill），**但它给"让 agent 自己写技能库"放了一个很硬的路标**——而那正是 deck 附录 GEPA / ACE 的方向。

🔑 **成熟度模型里 2 → 3 那一跳（评测与治理）现在有实证分量了：没有策展的增长，实测是负收益。**

---

## 相关

- [`notes.zh.md`](notes.zh.md) —— 主讲 Skillcraft 逐幕笔记
- [`lab-log.zh.md`](lab-log.zh.md) —— Genie's Kitchen 实操记录
- [`lesson-plan-精读.zh.md`](lesson-plan-精读.zh.md) —— lesson plan 逐节精读
- [[SRA 论文精读笔记]] —— 本页多处引用的实测来源
- [[Voyager 论文精读笔记]]
- [`../reading-list.zh.md`](../reading-list.zh.md) —— 参考资料 deck 的六类清单已并入
