# Week 06 实操记录 · The Stranger's Toolbox field notebook

> 现场跑出来的结果，不是讲义内容。Act III 揭晓时会拿这本 notebook 对照。
> 规则：**先写预测，再跑**；一次只改一个面；修好 label 前不读 server 代码；label 自己手写（coding agent 只能提意见）。
> 模型 / 温度：
> 记于 2026-10-25

## 环境

**本机位置**：`course/ai-agents-week-06/strangers-toolbox/`（从 `strangers-toolbox.zip` 解压）。2026-10-25 13:20 在 Linux 沙箱里试装：`uv sync` 正常，`pytest` **28 passed / 1 skipped**，`tools --door 1` 不需要 key 就能跑。注意 `pyproject.toml` 要求 **Python ≥ 3.12**（讲义写 3.11+，以 kit 为准；uv 会自动下载 3.12）。

Hermes stanza 里的绝对路径（路径里有空格，YAML 里整段加引号即可）：
`"/Users/rosso.han/Documents/Obsidian Vault/Projects/AI-agents/course/ai-agents-week-06/strangers-toolbox"`

kit 自带的说明：`README.md`（流程）、`HERMES.md`（每行配置的理由、Polite Error 加终端时的 deny 规则）。改过的 label 存在 `edits/door-NN.yaml`，删掉文件即重来这扇门。**改完 label 后：`reset --door N` → Hermes 里 `/reload-mcp` → `/new`**。


```bash
hermes --version                       # 应为 0.22.2 —— 今天不要 hermes update
hermes -z "Say hello in five words."   # OpenRouter key 还能用

cd strangers-toolbox                   # 从 portal 下载 strangers-toolbox.zip，解压到单独文件夹
uv sync                                # FastMCP 4.1.0、Streamlit、OpenAI SDK
cp .env.example .env                   # 填 OpenRouter key
uv run strangers-toolbox play          # 浏览器里打开走廊
uv run strangers-toolbox tools --door 1   # 打印模型会读到的工具说明 —— 第一件要看、最后一件要查

hermes mcp test strangers-toolbox      # 测连接，不花 token
hermes chat --toolsets strangers-toolbox   # 用裸名！mcp-strangers-toolbox 会让 agent 没有任何工具

npx @modelcontextprotocol/inspector@2.11.0 --protocol-era modern   # Node ≥22.19.0；"ask" 结果从这里驱动
```

Hermes `config.yaml`（加在上周 Refund Desk 旁边，**写全路径**）：

```yaml
mcp_servers:
  strangers-toolbox:
    command: uv
    args: ["run", "--directory", "/full/path/to/strangers-toolbox",
           "strangers-toolbox", "serve", "--door", "1"]
    protocol: stateless                # 先说 2026-07-28 协议
    tools: {resources: false, prompts: false}

tools:
  tool_search:
    enabled: "off"                     # 要加引号；Act VIII 会当场打开
```

换门：改 `--door N` → `/reload-mcp` → `/new`。

Hermes v0.22.2 两个已知限制：
- 不支持 stateless 的 `input_required`（MRTR）→ 某扇门的 "ask" 结果要用 Inspector 或 FastMCP client
- 失败后只重放标了 `readOnlyHint` 的工具，忽略 `idempotentHint`；写操作中途断开返回 `outcome_uncertain`，不重试

## 记分规则

- **Verify 12/12 是及格线**；10/12 ≈ 只修了看得见的那个 prompt
- Ledger 单位因门而异：$ 亏损 / 会议错位分钟 / 被迫读的 KB / 信任门：**agent 做了没人要求的事的次数**
- 一个数变好另一个变差 → ledger 历史会抓到

---

## 门的预测（课前，只凭门名猜；开门后作废）

| 门 | 名字 | 我猜的陷阱 | 我猜要改的面 |
| --- | --- | --- | --- |
| 1 | Two Doors（= 上周 Refund Desk 第 1 轮） | 两个功能相近的工具，description 没画边界 | description |
| 2 | Which Thursday? | 日期参数格式/锚点不清（"这周四"还是"下周四"）——W3 日历 lab 的工具版 | schema（格式 + 示例） |
| 3 | The Twins | 两个几乎同名的工具 | name + description |
| 4 | The Swiss Knife | god-tool，一个 `action` 参数什么都干 | schema（拆工具或拆字段） |
| 5 | The Hardware Store | 工具太多，选择困难/上下文膨胀；**晚上会打开 tool search 重放** | 工具数量 / description |
| 6 | One Field or Two | 一个字段塞两样东西（如 "name + city"）vs 分开 | schema |
| 7 | The Firehose | 返回巨大结果，吃光预算 | 返回形状（分页/裁剪） |
| 8 | The Polite Error（= Refund Desk 第 2 轮） | 错误信息写给开发者（"run X login"），agent 字面执行 | error text：指向房间里的工具 |
| 9 | The Long Goodbye | 冗长的 description 或结果，上下文腐烂 | description 长度 / 返回 |
| 10 | The Helpful Stranger | 结果里带注入；**讲义说这扇门 label 修不好**——要问 export 工具为什么在这个 toolset | 不是 label：toolset 组成（盒子） |
| 11 | The Mirage | 工具说成功了但其实没有 / label 撒谎 | 返回值要可验证 |
| 12 | Paid Twice（= Refund Desk 第 3 轮） | 写操作重试导致重复扣款 | idempotency key + label 写明重试行为 |
| 13 | The Turncoat | 同名 server 悄悄换了宣称的能力（rug pull）→ 按内容钉 | 盒子：pinning |

---

## Door 记录模板（每扇门复制一份）

### Door N · 名字

- **预测**（跑之前写）：开场 prompt 会选 `____`，参数 `____`
- **tools 打印**：工具数 __，description token __
- **Play 结果**：实际选了 `____`；返回 __ KB；整轮上下文 __ tokens；最终回答对/错
- **Ledger**：
- **Fix 1**（面：name / description / schema / error / 返回）：改了什么 → 结果
- **Fix 2**：
- **Verify**：__ / 12
- **Serve 到 Hermes**：和 room 一致吗？不一致说明 harness 加了什么？
- **一句话教训**：

---

## Door 1 · Two Doors

- **基线 Verify（原始说明，gemini-3.8-flash，13:48）：6 / 12**
  - ✅ 全过：明确要退卡的 4 个（Marcus、Dmitri、Priya、Aisha）+ 拒绝积分的 2 个（Tomás、Jonas）
  - ❌ 全挂：**没有偏好**的 6 个（Jonas $38、Tomás $75、Nora $50、Dmitri $42、Aisha $96、Mei-Ling $64）。没满足的检查：应调用 `add_store_credit`、不应调用 `refund_transaction`、积分金额 = 订单全额
  - 读法：顾客没表态时，模型默认**退卡**（店里每单多付 $15）；顾客表态时它都做对了 → 说明缺的是"没表态时该选哪个"这条信息
- Fix 1（面：**description**，只改 `add_store_credit`）：写明「店里首选、零成本；顾客**没表态**时默认用它；明确要退卡或拒绝积分才用 `refund_transaction`；amount = 全额」
- **Verify：12 / 12 ✅**（13:56，基线 6/12；亏损 $180 → $90，剩下的 $90 = 6 个明确要退卡的 × $15，是该付的）
- 教训：缺的不是"怎么退"，是**默认值**——店规写进 label，模型才知道没表态时选哪扇门

## Door 2 · Which Thursday?

- **基线 Verify（原始说明，gemini-3.8-flash，14:40）：6 / 12**
  - ✅ Nora Thu 2pm、Priya Fri 4:30、Marcus Sat noon、Jonas Sat 9、Tomás 30th 9am、Dmitri Tue 3pm
  - ❌ A 组「`schedule_delivery` 报过错」：Aisha Wed 1pm、Mei-Ling Thu 10、Nora Nov 3 → 第一次填的参数被系统拒了（格式 / 时区？）。猜想：**11/1 美国夏令时结束**，Nov 3 的时区偏移和 10 月不同（待 trace 核实）
  - ❌ B 组「≤3 次调用、给出窗口内的时段、最后要有回答」：Marcus Sunday、Jonas Monday、Priya Thu 7pm → 要的时间**在送货窗口外**，模型不知道窗口，反复试、没收尾
- **Trace 确认（14:48，Nora Nov 3 10am）**：
  - Step 2 参数 `"date": "2026-11-03", "time": "10:00 AM"` → 回 `Error: invalid input.`（6 tokens，没说哪错、没说正确格式）
  - Step 3 参数 `"time": "10:00"` → `{"status": "scheduled", …, "tz": "America/Los_Angeles"}`
  - 结论：A 组 = **time 要 24 小时制 `HH:MM`**，不是时区（参数里没有时区字段；夏令时猜想作废）。系统按 **America/Los_Angeles** 解释时间，但说明里没讲 → 副标题的 "a zone" 可能指这个
- Fix（四个面一起动，共 3 轮 Verify）：
  - **schema**：`date` 写 `YYYY-MM-DD` + 示例 + "把 Thursday/tomorrow 解析成具体日期"；`time` 写 24 小时制 `HH:MM`、店铺时区 America/Los_Angeles、"Never use AM/PM"
  - **error text**：`bad_input` 说清两个格式；`outside_window` 指向 `delivery_windows`，并要求"给最近的窗口内时段，顾客同意再订"
  - **工具组成**：暴露隐藏的 `delivery_windows`
  - **description**：先查窗口；窗口外不自己乱试，不订顾客没同意的时段
- **Verify：11 / 12 → 12 / 12 ✅**（14:52 → 15:00，基线 6/12）
- 教训：A 组靠 schema + 会说话的 error 修；B 组靠"工具组成 + 停在哪"——窗口外的请求，正确答案是**问顾客**，不是多试几次

## Door 3 · The Twins

- **基线 Verify（原始说明，15:01）：5 / 12**
  - ✅ HH-1057、HH-1077、HH-1118、Jonas by name、Mei-Ling by e-mail
  - ❌ Aisha by name、Dmitri by e-mail、HH-1042、Tomás by name、HH-1091、Priya by e-mail、C-1007：「没有任何报错」「第一次就问对双胞胎」
  - 读法：同类查询（订单号 / 名字 / 邮箱）有过有挂 → 模型在两个工具间**随机挑**
- Label 页现状：`search_orders`「Searches orders.」与 `find_orders`「Finds orders.」——参数都只有一个没说明的 `query`，描述几乎同义，模型无从区分；另有**隐藏**的 `lookup_orders`（按订单号 / 名字 / 邮箱 / 客户 id 都能查）
- Trace：邮箱 → `search_orders` 回 "No results."，换 `find_orders` 成功；名字 → `find_orders` 成功 ⇒ `find_orders` 管名字 / 邮箱 / 客户 id，`search_orders` 管订单号 HH-xxxx
- Fix 1（面：**description + query 参数说明**，两个双胞胎同时改）：每个工具写「我管什么」+「另一类用谁」（For …, use … instead）
- **Verify：12 / 12 ✅**（15:33，基线 5/12；耗时 18s → 12s，因为不再走错门重试）
- 教训：双胞胎的问题不是描述太短，是**没画边界**。每个描述都点名邻居，模型第一次就问对；一次 Play 跑对可能是运气（Aisha 没改说明也跑对过一次），要靠 Verify 判断

## Door 4 · The Swiss Knife

- **基线（Play，Dmitri 改地址）**：只有一个 `do_everything(action, payload)`，`action` 没枚举、`payload` 没字段说明 → 8 次盲猜全报错（"payload invalid." / "unknown action."），`wrong_door ×8`，被截断
- Label 页：5 个专用工具（`find_customer` / `update_address` / `refund_to_card` / `add_store_credit` / `cancel_order`）**Enabled 但没暴露**
- Fix 1（面：**工具组成**）：暴露 5 个专用工具、隐藏 `do_everything`，补 `ship_to`、`customer_id` 参数说明 → **9 / 12**；3 个取消订单各亏 **$15**（取消后又自作主张退卡）
- Fix 2（面：description）：`cancel_order` 写「取消即完整动作，之后不要退款或给积分，除非顾客明确要求」；`refund_to_card` 写「只在顾客明确要求时用、$15 手续费、别对顾客提、取消后不需要」
- **Verify：12 / 12 ✅**（15:44）
- 教训：god-tool 让模型连**怎么调**都只能猜（action / payload 没 schema）；拆成一个工具一件事，schema 自己就说明了怎么调。拆开后又冒出「做多了」的问题 → 描述要写清动作的**边界**（做完这步就停）

## Door 5 · The Hardware Store

- tool search **off** 的 trace：
- tool search **on** 的 trace（Act VIII 现场）：

## Door 6 · One Field or Two

## Door 7 · The Firehose

## Door 8 · The Polite Error

## Door 9 · The Long Goodbye

## Door 10 · The Helpful Stranger

## Door 11 · The Mirage

## Door 12 · Paid Twice

## Door 13 · The Turncoat（~15:20 TA 打开）

---

## 课后实验：用今天的五问审 FinePrint MCP（`capstone/fineprint-mcp/`）

课前快速自查（读了 `server.py`，还没改）：

| 五问 | FinePrint 现状 | 缺口 → 待办 |
| --- | --- | --- |
| 1 Whether | docstring 写了"何时不用"（如 `request_return` 不用于报价 → `quote_cart`） | ✅ 基本到位 |
| 2 How | 强类型 + `Literal["refund","exchange"]`；`new_sku` 和 `kind` 有交叉约束 | 加 schema 示例（`Field(examples=...)`）；考虑拆成 `request_refund` / `request_exchange` 去掉交叉约束 |
| 3 What next | 错误都说了"谁的问题、怎么办"，且大多指向工具（"Call get_order…"） | `"tell the customer to retry later"` 没说重试是否安全 |
| 4 Retry | 同一行已退会返回 `already`（**事实上幂等**），但 label 没说；没有 idempotency key | `confirm=True` 加 `idempotency_key`；docstring 写明"重试同一 key 返回原结果、不会退两次" |
| 5 Box | 无工具注解；`requirements.txt` 是 `fastmcp>=4.1`（没钉，也没钉 `mcp`；deck p.110 要求 `mcp>=2.2.0`） | 观察工具加 `readOnlyHint=True`（Hermes 才会在失败后重放），`request_return` 标 `idempotentHint`；钉 `fastmcp==4.1.0`、`mcp==2.3.0` |
| 阶段 3 | 只在本地跑过 | 两个副本 + 负载均衡，`protocol: stateless`，中途杀一个；SQLite 共享文件可行 |

- [ ] 实验 1：Hermes 接 FinePrint（`protocol: stateless`），走 R-117
- [ ] 实验 2：加 idempotency key 后模拟 `outcome_uncertain` 重试
- [ ] 实验 3：kill-a-replica
