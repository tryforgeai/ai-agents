# Week 06 听课速览（2026-10-25）

**Toolcraft, Part II — The Plug, the Doors and the Protocol**（讲义 27 页，Asif Qamar，first draft 2026-10-25）
原文：[uploads/fall-agents-week-6-lesson-plan.pdf](uploads/fall-agents-week-6-lesson-plan.pdf)

> 今日论点：**The protocol carries capability; the architecture around it carries trust.**
> 十二扇门要教的：**Labels request. Boxes enforce.**（标签只能请求，盒子才能强制）

## 时间线

| 时间 | 环节 | 内容 | 形式 | 笔记位置 |
| --- | --- | --- | --- | --- |
| 11:00–11:15 | Arrival | 早餐；上周欠的 credits；谁把工具注册进 Hermes 了？ | 全体 | — |
| 11:15–11:35 | Where We Left Off | **复述：label 决定的四件事**（见下） | Say-it-back | notes §0 |
| 11:35–12:00 | Preface · The Plug and the Ledger | NIM crate；2026 三件事；新型用户；三个问题、五个决策；drop-off point | Deck | notes §1 |
| 12:00–13:30 | 十二扇门 1–6 | Clarity + Scope：play → 读 trace → 改 label → verify → serve 到 Hermes | 动手 | lab-log |
| 13:30–14:05 | 午饭 | 35 分钟 | — | — |
| 14:05–15:30 | 十二扇门 7–12 | Politeness + Trust；第 13 扇门 ~15:20 由 TA 打开 | 动手 | lab-log |
| 15:30–16:00 | Act III · What the Doors Were Teaching | 揭晓：四个面、一条礼貌规则、label 到哪为止 | Deck | notes §3 |
| 16:00–17:30 | Acts IV–VII | 协议传记；stateless turn；长回来的扩展；bazaar 与账本 | Deck | notes §4–7 |
| 17:30–17:45 | 休息 | | | |
| 17:45–18:30 | Interlude + Acts VIII–IX | 深度的半衰期；两条轴不是梯子；procedure 走线上 | Deck | notes §8–9 |
| 18:30–19:15 | Acts X–XI + Coda | 盒子 fail open；toolwright 五问；回到 Beck 地图 | Deck | notes §10–11 |
| 19:15–19:45 | Questions | 答疑 + 作业 | 全体 | index 待办 |

落后时的压缩：Half-Life 变一页；Bazaar 只留"每个数字都要带单位"和"同名不同服务器"；bash 结果一页 + Willison 对照。**门和 Act X 不砍。**

## 11:15 复述题 —— 先自己默写

一个工具的 label 决定四件事（上周 debrief 画成一条线上的四个站）：

1. **是否被调用**（whether）—— description 决定
2. **怎么被调用**（how）—— schema 决定
3. **失败后下一步做什么**（what next）—— error text 决定
4. **重试会发生什么**（what a retry does）—— 幂等性要写进 label

✅ deck p.5 官方答案：四站 = **the description**（whether：调它还是调邻居？）· **the schema**（how：哪些字段、什么形状）· **the error**（what next：失败后走哪扇门）· **the contract**（what a retry does：一次还是两次？）。第四站叫 **contract**——幂等 key 是契约的一部分，不是全部

## 课前检查（**今天不要 `hermes update`**）

- [ ] `hermes --version` → **0.22.2**；`hermes -z "Say hello in five words."` 能通
- [ ] 自己的 server 钉版本：`fastmcp==4.1.0`、`mcp==2.3.0`、Python ≥3.11，每个 server 一个独立 uv 项目，**不要装进 Hermes 的环境**（Hermes 自带 mcp 2.0.0）
- [ ] 从 portal 下载 `strangers-toolbox.zip` → 解压到单独文件夹 → `uv sync` → `cp .env.example .env` 填 OpenRouter key → `uv run strangers-toolbox play`
- [ ] **课前不要开任何一扇门**
- [ ] Hermes 配置加 strangers-toolbox stanza（`protocol: stateless`，`tool_search.enabled: "off"`，见 lab-log）
- [ ] `hermes mcp test strangers-toolbox` 不花 token；`hermes chat --toolsets strangers-toolbox`（**用裸名**，不要用 `mcp-strangers-toolbox`）
- [ ] Node ≥22.19.0，备好 `npx @modelcontextprotocol/inspector@2.11.0 --protocol-era modern`（"ask" 结果要从 Inspector 或 FastMCP client 驱动，Hermes 不支持 `input_required`）
- [ ] 投影时别让 OpenRouter key 露出来；上周露过的要轮换

## 主线（三句话）

1. **插头的论证**：N×M 个定制集成 → N+M。标准的价值和它决定的东西之少成正比（NIM crate、USB、MCP）
2. **label 就是 prompt**：name / description / schema / error text 四个面 + 第五面"返回值"；前 9 扇门靠写得更好就能修
3. **写到哪为止**：后 3 扇门（+第 13 扇）证明 label 只能请求，registry / gateway / harness / sandbox 四个盒子才能强制，而且盒子自己也会 fail open
