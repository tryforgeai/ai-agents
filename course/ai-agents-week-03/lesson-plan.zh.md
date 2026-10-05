# Week 03 听课速览 · Skillcraft

> 来源：[Week 3 lesson plan](fall-agents-week-3-lesson-plan.pdf)，Asif Qamar，初稿 2026-10-03。以下按讲义整理；页码指印刷正文页码（PDF 页序减 2），不将课堂预期写成实测结果。
>
> 📖 逐节精读版见 [`lesson-plan-精读.zh.md`](lesson-plan-精读.zh.md)——本文是速览，精读版补齐了公式算例、具体数字、排错表与 field notebook 模板。

## 一句话主线

**Skill 是等待需要时才拿出来的操作规程：description 决定何时使用，procedure 说明如何做，Done when 说明何时完成。** 确定性的步骤交给脚本，每一步都安排检查。

课程顺序已调整为 **本周 Skills → 下周 Tools → 自动提示词优化**。上周 Oracle prompt 和隐藏测试失败仍要保留。

## 课前准备（正文 pp. 3–4）

1. 从课程门户下载 `genies-kitchen.zip`，解压后进入目录，运行 `uv sync`、`uv run genies-kitchen`。默认地址为 `http://localhost:8501`；若 Strange Lamp 仍占用端口，先停止它。其他端口的参数以 app 帮助为准。
2. 在 sidebar 填入 OpenRouter key，或在本地配置 `.env`。不要把真实 key 写入笔记或版本库。
3. 准备可加载 skill 的 agent：Hermes 至少能运行 `hermes skills list`；讲义要求 Claude Desktop 开启代码执行与文件创建功能。界面名称按讲义记录，安装时以实际客户端为准。
4. 检查 Python：晚间脚本要求 **3.10+**；已有 `uv` 时可用 `uv run --python 3.12 python <script>`。讲义另注明 Windows 可能需安装 `tzdata`。

## 全天时间表（正文 p. 5）

| 时间 | 环节 | 重点 |
| --- | --- | --- |
| 11:00–11:15 | Arrival | 凭记忆重建 Week 02 地图 |
| 11:15–11:35 | Prologue · Harrison’s Clocks | 长期留下来的是可复用的做法 |
| 11:35–12:20 | I · Foundations | skill 的定义、三层结构、生命周期 |
| 12:20–13:30 | Genie’s Kitchen | Literal Cook / Which Scroll Wakes? / Context Window |
| 13:30–14:05 | 午饭 | 35 分钟 |
| 14:05–15:10 | II–III · Theory / Lineage | 加载规则、Options、Voyager；The Bazaar |
| 15:10–16:15 | IV–VI · Practice / Patterns / Synthesis | 编写、测试、模式、系统；Run, Don’t Reason / The Forge |
| 16:15–16:25 | Coda · Hokusai | 实践后才能看见上一版的不足 |
| 16:25–16:40 | 休息 | |
| 16:40–18:15 | Lab · Samarra | 所有人先做 Tier 1 |
| 18:15–18:30 | Checkpoint | 拆步骤、放 verifier；发 Tier 1 参考 skill |
| 18:30–19:45 | 可选进阶 | Tier 2 / Tier 3 |
| 19:45–20:00 | 未见请求 | 展示 12 个隐藏案例 |

讲义延续上周的安排：没有总排行榜，以逐例阅读、判断和通过/失败标记学习；系统评测会在后续课程展开。

## 六幕重点

### I · Foundations：从一次提示到可复用做法（pp. 6–9）

- Tool 提供单次可调用能力；skill 包装一类任务的流程与判断；agent 在循环中决定下一步。
- RAG 提供 knowing-that（事实），skill 提供 knowing-how（做法）。
- Skill 的四个动作：**author / retrieve / compose / improve**。
- 三层渐进加载：常驻名称与描述；相关时加载正文；按需读取参考资料或运行脚本。
- 指令放在哪一层取决于使用时机：长期通用要求放 system prompt，偶尔用到的多步骤流程放 skill，变化的事实按需检索。

### II · Theory：加载也有成本（pp. 12–15）

- harness 组装上下文，model 提议动作，harness 执行或限制动作。
- 教学模型：`VoL(s) = p_s × g_s − κ(c_s)`，预期能力收益大于上下文稀释成本时才加载。
- 两个主要写作抓手：description 精准地区分请求；正文保持精简，将罕见分支外置。
- Skill 对应强化学习中的 option：**initiation set / policy / termination**，映射到 **description / procedure / Done when**。
- 复用流程缩短规划跨度，但子流程完成并不免除父流程自己的检查。

### III · Lineage：从调用能力到积累经验（pp. 16–19）

- Toolformer / Gorilla：调用工具。
- Voyager：自动课程、可检索的代码技能库、自验证；改进积累在外部技能库，而非必须更新模型权重。
- Reflexion / ExpeL：把失败反馈变成可复用的文本经验。
- Agent Skills 格式：让流程成为可阅读、比较版本和迁移的文件夹。
- 市场插曲：第三方 skill 同时带来**指令与代码**两类攻击面；正文和脚本都要审查，配合来源管理、测试和 sandbox。

### IV · Practice：最小能触发的 skill（pp. 19–22）

- description 写“做什么、何时用、何时不用”，采用用户实际会说的词。
- 正文放主路径；参考资料写清何时读取；脚本路径相对 skill 定位，执行时使用完整路径。
- 判断、歧义处理、表达交给模型；重复且正确性关键的确定性工作交给代码。
- **Firing test** 测是否选对；**behaviour test** 测加载后是否完成任务。
- 发布后记录：是否触发、是否有帮助、成本多少、是否与别的 skill 冲突。

### V · Patterns：按问题选结构（pp. 23–25）

| 问题 | 模式 |
| --- | --- |
| 正文越来越长 | Lean Core + Appendix |
| 多份副本逐渐漂移 | Single Canonical Source |
| 长流程容易漏步骤 | Checklist-Carrier |
| 输出必须匹配固定结构 | Template-Bearer |
| 不知何时停 | Definition-of-Done |
| 硬约束不可违反 | Guardrail 与升级处理 |
| 两个 skill 抢同一请求 | Router |
| 后果重大、难撤回的动作 | Dry-Run；配合幂等设计 |
| 需要外部数据或能力 | Skill + MCP |

常见坏味道：Kitchen-Sink（什么都塞正文）、Silent（不触发）、God-Skill（什么都接）、Collision（触发冲突）、Stale（过期失管）。

### VI · Synthesis：放回整个 agent 系统（pp. 25–27）

Agent loop、router、loader、技能库、tools/MCP、governor 与可观测性共同工作。区分 **访问能力、操作流程、选择机制、治理**。

讲义的升级阶梯：`prompt / skill → prompt optimization → retrieval → supervised fine-tuning → reinforcement learning`。先尝试成本低且足够的层；以失败证据支持升级。

组织成熟度：临时提示 → 写成技能 → 整理成库 → **评测与治理** → 自我改进。技能数量增长必须配上评测与治理。

## Kitchen 六个实验

| Tab | 操作 | 要观察的东西 |
| --- | --- | --- |
| The Literal Cook | 预测流程漏洞、运行、修补，补上 Done when | 停止条件、输入、排除项、数量、顺序、结果检查六类缺口 |
| Which Scroll Wakes? | 改一个 description，先测 8 个已知请求，再测 8 个隐藏请求 | 漏触发、误触发、相邻技能冲突；none 也可能是正确答案 |
| The Context Window, Live | 逐次看 load / read / answer，再比较全部一次加载 | token 增长、无关指令污染、harness 与模型的分工 |
| Run, Don’t Reason | 五类计数/日期/求和任务，模型和脚本各运行 10 次 | 一致性、正确性、输入解释是否可靠 |
| The Bazaar | 查看并安装课堂摊位，比较 Audit 与 sandbox | 描述承诺和正文行为是否一致；外传能力是否被切断 |
| The Forge | 填 name / description / body，校验后生成 zip | 格式错误与写作建议不同；能打包不等于行为正确 |

## 晚间 Lab：An Appointment in Samarra（pp. 28–36）

Zara Malik 转发一条约会消息，再说 **“Put it on my calendar.”**。创建名为 `when-the-time-is-right` 的 skill，输出三类结果之一：

1. 正确会议、正确时间的 `.ics` 邀请文件。
2. 说明为什么不能安排，并提供可行时间。
3. 信息不足时问她一个问题。

**交付物是邀请文件，不是自动发送邀请。** 讲义把这种先给文件、由人决定使用的做法视为 Dry-Run。

### 材料与难度

16:40 从课程门户获取 `when-the-time-is-right-kit.zip`，先读 `brief.pdf`。

| 材料 | 用途 |
| --- | --- |
| `owner/profile.md` / `owner/calendar.ics` | Zara 的规则与已有日历 |
| `cases/given.md` / `cases/given.jsonl` | 100 个公开案例及正确结果；它们也是规格的一部分 |
| `check.py` | 对单个案例判定，不给总分 |
| `drawer/` | 时区转换、节假日查询、工作日计数、邀请文件生成四个脚本 |
| `when-the-time-is-right/` | 待编写的 skill 文件夹 |
| `pack.py` | 打包并检查部分结构规则 |

- **Tier 1：**读懂请求。18:15 前全员集中这一层。
- **Tier 2：**时区与节假日。
- **Tier 3：**Zara 的日历和个人规则。
- 另有 100 个保留案例；19:45 展示其中 12 个。它们并未包含在当前 lesson plan 中。

```bash
python3 check.py g-017 --show
python3 check.py g-017 --invite my-invite.ics
python3 check.py g-020 --ask day
python3 check.py --help
```

### 打包和跨 agent 验证

按讲义的实验兼容约束：名称与目录名一致，最多 64 字符，用小写字母、数字和连字符；description 最多 1,024 字符且不含尖括号；包内只有一个大写 `SKILL.md`；front matter 先只用 `name` 和 `description`；脚本使用 Python 标准库。

`.skill` 本质是 zip，**根层必须保留 skill 文件夹**，不要只压缩文件夹内的散文件。运行 `python3 pack.py when-the-time-is-right` 会生成 `.skill` 和 `.zip`。

讲义中 Hermes 从本机 `~/.hermes/skills/` 加载，修改后新建会话或 `/reset`；Claude Desktop 通过 Skills 界面上传，在独立 sandbox 内运行。因此所有依赖资料必须随包携带，不能假定能访问本机其他文件或网络。skill 目录保存代码与资源，输出写到工作目录。

上述为课程流程摘要，尚未执行安装；客户端入口和格式兼容性以实际环境为准。

### 现场笔记模板

| 发现的步骤 | Reason / Run | 输入与假设 | 检查方法 | 案例及结果 |
| --- | --- | --- | --- | --- |
| 待实验填写 | | | | |

失败时额外记录：**案例编号 → skill 假设了什么 → 原消息其实没有说什么 → 如何修复和验证**。只做好 Tier 1 并诚实指出能力边界，比自信生成错误邀请更符合本次实验目标。

## 作业与阅读（pp. 36–39）

1. 在 Hermes 和 Claude Desktop 安装同一 skill，各运行同样三个案例，比较触发与行为。
2. 带步骤清单和踩坑记录参加 TA session，对照完整解法与 *What Did We Miss?*。
3. 从自己工作中选一个重复流程，写触发与排除、步骤、Done when；经 Literal Cook 检查后打包安装。
4. 选做：安装前审查一个公开市场 skill，用两行写出它在本机能做什么。
5. 选做：对工作日计数任务，用最强可用模型关闭/开启展示推理，各做 20 次短调用；比较结果及一次错误的后果。

**讲义列出的必读：** Agent Skills 开放格式、Voyager、Sutton 等人的 Options 框架、PAL、Simon Willison 的 *The Lethal Trifecta for AI Agents*。

**选读：** *Longitude*、Reflexion、ExpeL、*Lost in the Middle*、ToxicSkills、*The Timeless Way of Building*、RFC 5545，以及后续优化课相关的 GEPA / ACE。这里整理阅读方向，未对外部资料逐篇复核。
