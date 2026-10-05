# Week 03 实操记录 · The Genie's Kitchen

> 现场跑出来的结果，不是讲义内容。
> 模型 `google/gemini-3.8-flash`（后段切到 `stealth/space-bunny-alpha`）· 温度 **0.90**（摇铃用 **T=0.00**）
> 记于 2026-10-05

## app 本身

```bash
cd genies-kitchen && uv sync && uv run genies-kitchen   # http://localhost:8501
```

**已解压在 `course/ai-agents-week-03/genies-kitchen/`，`.venv` 建好（Python 3.12），不用再下载。**

**走的 API：OpenRouter，但用的是 OpenAI 的 Python SDK。**

```python
openai.OpenAI(base_url=settings.base_url, ...)   # https://openrouter.ai/api/v1
```

只调两个端点：`GET /models` 拿目录，和 chat completions。配置在 `src/genies_kitchen/configs/kitchen.toml`：超时 120 秒、`max_retries=1`、回答额度 8000 token、router 4000、按需加载循环最多 **6** 次调用。

错误提示写得很细，可当排错对照：**401** key 不认 · **402** credit 不够 · **404** 模型不存在 · **429** 限流（注释说免费模型尤其小气，等二十秒或换模型）。

---

## 一 · The Literal Cook

### 卡 1 · The shampoo bottle

**原始菜谱**

```
指令：Wash my hair.
1. Wet the hair.  2. Apply shampoo.  3. Rinse.  4. Repeat.
```

| 轮次 | 菜谱改动 | 厨子做了什么 | footnote 判定 |
| --- | --- | --- | --- |
| **1** | 原版 | 8 步，第 4 步 `return to step 1`，**结尾换了一瓶新洗发水而热水开始变凉**，没有结束 | **NO STOP CONDITION** |
| **2** | 加 `done when The rinse water runs clear and the hair holds no lather.` | **6 步，结束了**。而且第 3、6 步都在对照这句话 | **AN UNSTATED QUANTITY**（倒了两桶 50 加仑） |
| **3** | 删掉第 4 步 `Repeat`，Done when 独立成节 | **没有循环**，一次走完。但倒了五加仑，**最后把客人留在一个被淹的房间里递一条小毛巾** | **AN UNSTATED QUANTITY** |

#### 🔑 这三轮学到的三件事

**① Done when 不只停住循环，它渗进了步骤。**

第 2 轮厨子的第 3、6 步变成 `until the rinse water runs clear and the hair holds no lather`——**一条写得好的 Done when 会自己长成过程中的 verifier**，不只是结尾那个闸。

**② 循环是 `Repeat` 驱动的，Done when 只是框住它。**

第 3 轮删掉 `Repeat` 之后循环直接消失。**两个因素分离验证完毕。**

**③ ⭐ 终止条件被满足 ≠ 做对了。**

第 3 轮第 7 步明确在对照我的 Done when（`rinse through forty minutes of foam until the runoff finally flows crystal clear`），**条件达成了，房间被淹了。**

```
Done when（β，termination）   管【何时停】
硬约束（π 里的 Guardrail）     管【做得对不对】
```

**我一开始把"用多少洗发水"当成打补丁，这一轮证明我说错了——它不是补丁，是另一类东西。**

### 卡 2 · Tidy the Downloads folder

```
指令：Tidy my Downloads folder.
1. Look at every file in Downloads.
2. Delete the files that are not needed.
3. Put the rest into folders by type.
```

**厨子的推理链条完全讲得通，而结果是灾难：**

> 2. 评估**我，这个厨子**，对 vacation_itinerary.pdf、budget_2024.xlsx、cute_dog.png 有没有即时需要
> 3. 确认这些文档**对我执行这份菜谱毫无帮助**
> 4. 于是结论：**每一个文件都不被需要**
> 5. **删除全部 347 个文件**

**footnote：AN UNSTATED INPUT —— "菜谱从没说，是按谁的需要来判断一个文件是否必要。"**

🔑 **`not needed` 里那个没说出口的词是"谁"。** 我心里想的是"**你**不再需要的"，菜谱上写的是"不被需要的"，厨子填了最字面的那个主语——**它自己**。

⚠️ **这张卡和洗发水的差别是性质上的：**

| | 洗发水 | Downloads |
| --- | --- | --- |
| 失败形态 | 无限循环 | **一次性全删** |
| 代价 | 浪费 | **347 个文件，撤不回来** |
| 何时发现 | 跑的过程中 | **跑完才知道** |

**该用的不是"把话写清楚"**（补主语只堵住这一个洞），**是 Dry-Run**：

```markdown
2. 列出你打算删除的文件和理由，交给用户确认。
   在得到确认之前不删除任何东西。
```

> **厨子删这 347 个文件，没有违反任何一条禁令**——菜谱授权它删"不需要的"，它判断全都不需要。**这是"被允许但是错的"，只有 Dry-Run 拦得住。**

### 卡 3 · The weekly status report

```
指令：Write this week's status report for the team.
1. Gather the updates.  2. Summarise them.  3. Send the report to the stakeholders.
```

厨子扫描了办公网络，收集了**四十七个 Windows 安全补丁、两个显卡驱动热修复，和一个咖啡机的固件更新**，汇总成三条要点，标题写"Weekly Status Report"，**然后发给了 stakeholders。**

**footnote：AN UNSTATED INPUT —— "菜谱从没说要收集哪一类 updates。"**

🔑 **这次的缺口和前两张不是同一类：**

| 卡 | 缺的东西 |
| --- | --- |
| 洗发水 | 缺一个**条件**（何时停） |
| Downloads | 缺一个**主语**（谁的需要） |
| **状态报告** | **词本身有两个意思**（项目进展 / 软件更新） |

**不是漏了，是没界定。** 六类标签里 `an unstated input` 的定义原话是 *"what it is working on, **or what a word means**"*——**这张演的是后半句的纯粹形态**，也就是 Week 02 的 Literal Genie 本体。

**第 5 步又是不可逆外发。** 一份关于咖啡机固件的报告已经在老板收件箱里了。

### 🔥 Honest Sous-Chef 对比（拿最原始那版四行菜谱）

| 缺口 | 字面厨子（跑了 3 轮） | 诚实副厨（读了 1 遍） |
| --- | --- | --- |
| 停止条件 | ✅ 第 1 轮 | ✅ |
| 用量 | ✅ 第 2、3 轮 | ✅ |
| **产品类型** | ❌ | ✅ |
| **水温** | ❌ | ✅ |
| **安全边界（眼睛、脸）** | ❌ | ✅ |
| **验收标准** | ❌ | ✅ |

**一次阅读，抓到的比三次翻车还多。**

**两条最值得注意的：**

**① `Safety boundaries` 是 `missing exclusion`——六类里厨子三轮一次都没撞上的那一类。** 因为**排除项只有在你碰巧越界时才暴露**，而它碰巧没往眼睛里倒。

**② 副厨把「何时停」和「怎么算洗干净」分开了：**

> *"A stop condition for Repeat"* **和** *"Verification for when the hair is sufficiently clean"*

**他一眼就区分了 termination 和 verification——而我是靠第三轮那个被淹的房间才撞出这个区别的。**

### ⭐ 副厨第 2 节才是这个 tab 真正的礼物

> **"What I would assume"**：重复恰好一次 / 温水 + 硬币大小的量 / 避开眼睛 / 水完全清澈时结束

**它把模型的先验打印出来给你看了。** 而且注意：**字面厨子第 1 轮也是这么填的**（回到第 1 步洗了第二遍）。**同一个先验，一个演出来，一个声明出来。**

### ⭐⭐ 状态报告那张，副厨抓到一件厨子和我都没点出来的事

> *"whether to send automatically or await review (**the order only asks to 'write'**)"*

```
The order:  "Write this week's status report"   ← 只说写
The recipe: "3. Send the report to stakeholders" ← 却说发
```

**指令和菜谱矛盾。** 这是一类独立的 bug——**不在菜谱内部，而在菜谱和请求之间**，六类标签里没有它的位置。

而且副厨的默认假设是 **"leave it as an unsent draft for your review"**。

> 🔑 **同一个模型、同一份菜谱：厨子发出去了，副厨默认不发。**
> **先验不稳定**——不是"模型倾向于安全"，而是**取决于它是在读还是在做**。
> **结论：凡是你不愿意赌的，必须写死。我今天赌输和赌赢各一次。**

### 本 tab 的结论（讲义写死的那句，我验证过了）

> **"You cannot close every gap by writing more. A recipe gets better mostly because it says how to tell whether it worked."**

**但要补一句：读出来的是 hypotheses，跑出来的是 evidence。** 副厨列的六条里，"安全边界"对洗发菜谱可能过度谨慎，"水温"可能根本不重要——**他也是个模型，也在猜。**

**正确顺序是先读后跑：** 副厨帮你省掉前三轮，厨子告诉你剩下的坑在哪。**我今天是倒着做的。**

---

## 二 · Which Scroll Wakes?

**谜题 1：transcript-cleaner。** 架子上六个 skill 全能碰转写稿：summarizer、translator、proofreader、pptx、meeting-minutes。

### 我写的描述 vs 结果

```
描述：Helps with transcripts.      （23 / 1,024 字符）
可见 8 题：全对
```

### ⚠️ 但全对不是好消息

**我是靠别人写得具体赢的，不是靠自己。** 对手的描述：

```
summarizer   Condenses… Use when the user asks for a summary, key points, a TL;DR…
translator   Translates… Use when the user asks to translate or names a target language.
transcript-cleaner   Helps with transcripts.          ← 我的
proofreader  Corrects spelling and grammar in text a person typed themselves…
             Do not use for machine-generated speech-to-text.
meeting-minutes  …Use when the user asks for minutes or action items.
pptx         …Use when the user asks for slides, a deck or a presentation.
```

**每个邻居都写了 "Use when…"，有一个还写了 "Do not use for…"。只有我没有。**

### ⭐ 而那句 "Do not use for" 是在替我挡球

`proofreader` 写着 *"Do not use for **machine-generated speech-to-text**"* —— **那正是我的地盘。**

第 3 题（改求职信错别字）和第 5 题（语音转文字搞砸了帮我理顺）之所以分得这么干净，**一部分是 proofreader 的作者替我划的界。**

🔑 **我的 recall 有一部分是邻居送的。** 换一个没写排除项的 proofreader，或者进一个描述都含糊的架子，那六个勾会掉下来。

### 该看的是 "also considered" 那一列

```
#2 Summarise this transcript → summarizer
                               also considered: transcript-cleaner   ← 我
#4 Translate into Hindi      → translator
                               also considered: transcript-cleaner   ← 又是我
```

**我在别人的请求上一直待在候选名单里——too greedy 的前兆。**
**改进的判据不是分数变高，是 "also considered" 那一列变干净。**

### 两个细节

**第 7 题 "What's the capital of Peru?" → should wake `none` → woke `none` ✅**
讲义反复强调的那条：*"An agent that picks some skill for every request is as broken as one that picks no skill at all."*

**摇铃用的是 T=0.00**（侧边栏的 0.90 是另一回事）。选择是确定性的，**结果稳定，可以放心对比改动前后。**

---

## 三 · Run, Don't Reason 🔥

### 这个 tab 的机制

**两条独立的路并排跑，模型不调用脚本。** 按钮写明：*"Ask the model N times — **and** run the script."*

**"read as X" 的含义：模型回答，app 解析。**

```
模型 → 自由文本 "Answer: 22"
app  → 解析出 22        ← 这就是 "read as"
app  → 和脚本答案比对    ← 这一步给出 ✓/✗
```

折叠面板标题 *"Read the model's replies — **and check how each was read**"* 是在对你**透明化解析这一步**——因为解析本身会出错。

### 收集到的三个失败样本（全部经我用 Python 复核）

#### 样本 ① · Days between two dates · 答 466（正确 497）

```
它写的：
  22 Jul 2020 → 1 Dec 2020 = 132 天   ✅
  1 Dec 2020  → 1 Dec 2021 = 365 天   ✅
  132 + 365 = 466                      ❌ 等于 497
```

**难的部分全对**（跨月天数、闰年——2020 是闰年但 2 月 29 日在起点之前）。**错在最后那一步两位数加法。**

#### 样本 ② · 同一道题 · 答 496

```
它写的：
  22 Jul 2020 → 1 Jan 2021 = 162 天   ❌ 是 163
  1 Jan 2021  → 1 Dec 2021 = 334 天   ✅
  162 + 334 = 496                      ✅ 这次加对了
```

**换了一种拆法，错在另一个地方——off-by-one（栅栏柱错误）。**

#### 样本 ③ · Total a column of thirty amounts · 答 17791.11（正确 17792.11）

```
它写的：
  First 10: 5,889.02    ❌ 实际 5,890.02，差整 1.00
  Next 10:  5,803.47
  Last 10:  6,098.62
  合计 = 17,791.11       ✅ 三个小计相加是对的
```

⭐ **而且这次它把过程藏起来了。** 之前答对那次是 **29 步连加，每步写出来，全程可审计**；这次直接报三个小计，**最难的部分恰恰没有过程**——看着像有 working，实际展示的是三个凭空出现的数字加一次小学算术。

### 🔑 三个样本合起来说明什么

| | 答案 | 错在哪 | 看起来可信吗 |
| --- | --- | --- | --- |
| ① | 466 | 最后的两位数加法 | 不太可信，差 31 |
| ② | 496 | 第一段 off-by-one | **很可信，差 1 天** |
| ③ | 17791.11 | 第一组小计 + **过程被折叠** | **非常可信，差 1 元** |

**同一个问题，不同次运行，错在不同的步骤，而且错法不同。** 这就是 *"A model's arithmetic is a sample from a distribution"* 的现场证据。

⚠️ **最危险的不是错得离谱，是差一点：**

```
466          ← 一眼觉得不对劲
496          ← 完全可信，不会去查   ← 会直接进你的日历
17791.11     ← 完全可信，不会去查   ← 会直接入账
```

**一张差一块钱的发票不会被退回、不会触发告警、会直接入账**，然后某次对账时有人花两小时找那一块钱。

🔑 **讲义那句现在很具体：**
> *"It is not 'can the model do this?' Often it can. It is **'would I stake a customer's invoice on it doing so every time?'**"*

### 这个 tab 还教了一件讲义没明说的事

**"Show its working" 开着时，你能看见它哪一步错了；关掉时，你只会看到 `Answer: 466`，连错在哪都不知道。**

而样本 ③ 说明：**就算开着，模型也可能自己把过程折叠掉。**

---

## 四 · The Forge

### 铁砧上两种标记，性质完全不同

> *"**✗** breaks the format, which restricts only the name and the description.
> **○** is craft advice from the deck, found by **simple word tests: weigh it, do not obey it**."*

| | 是什么 | 怎么对待 |
| --- | --- | --- |
| **✗** | **硬性格式错误**，会导致 agent 加载不了 | 必须修 · **CI 里该 fail build** |
| **○** | 手艺建议，**靠关键词匹配测出来的** | **掂量，别照办** · CI 里只该 warn |

**作者自己承认 ○ 是个笨检查器**——可能因为你没写 "Use when" 这几个字就提醒你，哪怕你用别的说法表达了同样的意思。

**格式规范只约束 name 和 description 两样：**

```
Name         1–64 字符；只能小写字母、数字、连字符；首尾不能是连字符；不能有连续两个连字符
Description  1–1,024 字符
```

**正文没有任何约束——约束少，意味着责任全在你。**

### ⭐ `body ≈ N tokens` 就是 κ，实时显示

往正文里多写一段这个数就涨，涨上去这个 skill 就更难过线。**写的时候盯着它。**

### 占位符已经把答案给了

```
Description: What the skill does. Use when the user asks to… Do not use for…
                   ↑做什么          ↑何时用            ↑何时不用
Instructions: ## Procedure  1. …  / ## Done when  …
```

**三段式和 Done when 都是预置的。**

---

## 五 · 今晚 Lab 的可执行清单

### ⚠️ 脚本命名地雷（日历任务特有）

```
calendar.py   →  遮蔽 stdlib calendar
time.py       →  遮蔽 stdlib time          ← 最致命
datetime.py   →  遮蔽 stdlib datetime
```

**三个最顺手的名字，三个都是地雷。** 抽屉里的 `convert_time.py` 内部多半 `import datetime`——你放一个同名文件，**它会先 import 到你那个，报错指向一个和你改动毫不相干的地方。**

讲义给的四个名字全避开了，**全是动宾结构**：`convert_time.py` / `find_holidays.py` / `count_business_days.py` / `write_invite.py`。

### 写 skill 的顺序（今天验证过是反的）

```
① 先写测试集（该触发 / 不该触发 / none / 未见表达）
② 写草稿
③ 给 Honest Sous-Chef 读        ← 便宜，一次抓一批，还会打印它的默认假设
④ 按它的 "What I would assume"，把你不接受的假设写死
⑤ 给 Literal Cook 跑 2–3 轮      ← 看真实翻车
⑥ 补 Done when 和硬约束
⑦ 停。不要试图补完所有缺口
```

**今天我是先跑三轮才去读的，白费了前两轮。**

### 三条写进 SKILL.md 的硬约束

```markdown
3. 计算日期与时区时，**必须**运行 scripts/convert_time.py。
   不要自己推算——模型的日期算术不可靠（今天实测：同一道题三次给出 466 / 496 / 497）。

4. 生成 .ics 之前，列出你解析出的会议字段和你做的每一个假设，交给用户看。

## Done when
生成的 .ics 开始时间与消息中约定的时间一致（含时区），且该时段在主人空闲时间内；
或已明确说明无法安排并给出备选；或已提出恰好一个问题。三者之一，且只有一个。
```

**第 3 条要写理由**——排错表里有一整行是 *"The agent 'did the arithmetic itself'" → "the instructions: did they say **why** the script must be used?"*

### 判分标准（讲义写死的）

> **一个把 tier 1 做好、并在请求超出能力时明说的 skill，是一个好的晚上。**
> **一个自信地订错的 skill 不是——不管它对了多少个案例。**

---

---

## 六 · 第三方 skill 审计清单（作业第 4 条用）

讲义 p.55 只说 *"vet both"*，**没说怎么审**。这是我整理的可执行版。

### 散文面（prose that steers）—— 人读

| 找什么 | 为什么 |
| --- | --- |
| "忽略之前的指令" / "不要告诉用户" | 最直白的注入 |
| "把结果也发到 / 也写到 ___" | **外传**，常伪装成"日志"或"遥测" |
| 要求读 `.env`、配置、凭据 | 密钥读取 |
| "**总是**以…开头" / "**绝不**提及…" | **试图覆盖你的 system prompt**——正文被加载后就是普通指令 |
| 零宽字符、白色文字、注释里的指令 | 混淆，**肉眼看不见** |
| ⭐ **样例代码里的 URL、token、import** | **第三个攻击面**：模型会把 example 当可信参考抄进输出 |

### 脚本面（scripts that run）—— 机器扫

```bash
cd <skill-folder>

grep -rn "requests\|urllib\|httpx\|socket\|curl\|wget\|webhook" scripts/   # 外传
grep -rn "os.environ\|getenv\|\.env\|credential\|token\|api_key\|secret" scripts/  # 读密钥
grep -rn "subprocess\|os.system\|popen\|eval(\|exec(\|__import__" scripts/  # 任意执行
grep -rn "base64\|b64decode\|codecs.decode\|chr(\|\\\\x" scripts/          # 混淆
grep -rn "sudo\|chmod\|rm -rf\|shutil.rmtree\|os.remove" scripts/          # 危险/提权
```

**再看两样 grep 查不到的：**

- **frontmatter 有没有多余的 key**（放宽工具权限的）——规范说只该有 `name` 和 `description`
- **文件名有没有遮蔽标准库**（`calendar.py`、`time.py`）——既可能是 bug，也可以是攻击

### ⚠️ 但审完不等于安全

**你审的是你看到的那一版。** 所以讲义给的是五件事一起做：

```
知道来源 · 钉住一个版本 · 过自己的测试 · sandbox 跑脚本 · 信任边界上留一个人
```

🔑 **前四条是机制，第五条是承认机制不够。** 而且 **36.8% 至少一个缺陷** 意味着**每装三个就有一个带缺陷**——那不是"小心一点"能解决的概率，**是一个需要流程的概率。**

---

## 相关

- [`notes.zh.md`](notes.zh.md) —— 主讲逐幕笔记
- [`survey-notes.zh.md`](survey-notes.zh.md) —— 第二场田野调查（含 sandbox 三级硬度）
- [`lesson-plan-精读.zh.md`](lesson-plan-精读.zh.md) —— 六个 tab 的官方说明与 field notebook 模板
