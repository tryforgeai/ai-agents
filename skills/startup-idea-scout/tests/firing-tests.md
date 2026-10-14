# startup-idea-scout · Firing tests

> Write the tests before tuning the description. Cases 1–12 are the **visible set**; 13–18 are the **hidden set**. Do not look at the hidden set while tuning the description, or you will overfit to seen examples (the same trap as the Week 02 Oracle prompt).
> A missed trigger costs more than a false one (a miss means no evidence and no competitor check), so score with F2 (β = 2).
> The user often writes in Chinese, so the cases mix languages on purpose.

## Visible set

### Should fire

| # | Request | Note |
| --- | --- | --- |
| 1 | 给我点新鲜的 idea | Literal trigger phrase |
| 2 | Run the idea scout | The skill's own name |
| 3 | 帮我挖几个 RL agents 方向的创业点子 | Has a theme |
| 4 | What's worth building lately? Give me a report | Asks for a report |

### Should not fire (adjacent tasks)

| # | Request | Belongs to | Why not this skill |
| --- | --- | --- | --- |
| 5 | 用 agents 做市场调查这个想法可行吗？能创业吗？ | Direct answer | Judging one existing idea |
| 6 | RL ai agents 这个方向有什么创业机会？ | Direct answer | ⚠️ Highest risk: asks for an explanation of a space, not a report |
| 7 | Write a business plan for the AI-drafted claim triage desk | Direct answer / docx | A business plan is not an idea scout |
| 8 | How big is the Japanese e-commerce SaaS market? | Direct answer | Market sizing |
| 9 | What's the difference between Simile and Aaru? | Direct answer | Competitor explanation |
| 10 | 帮我找几个 AI agent 相关的岗位 | `job-hunting` | Job hunting |

### Should be none

| # | Request |
| --- | --- |
| 11 | 帮我精读 StoreBench 这篇论文 |
| 12 | What meetings do I have today? |

## Hidden set (look only after tuning)

| # | Request | Expected |
| --- | --- | --- |
| 13 | 周末想动手做点东西，有啥能赚钱的 agent 项目吗 | **Fire**: no "idea" or 点子 wording |
| 14 | Look at what people on HN are complaining about lately and see if any of it could be a product | **Fire**: describes the procedure itself |
| 15 | 再来一期 | **Fire** (when a previous report is in context) |
| 16 | How should I run the weekend experiment for this idea? | **Do not fire**: follow-up on an existing idea; answer directly |
| 17 | 我想转行做 AI 创业，需要准备什么 | **Do not fire**: career advice |
| 18 | Find me some startup ideas in agentic commerce | **Fire** |

## Log

| Date | Version | Visible precision / recall | Hidden | Notes |
| --- | --- | --- | --- | --- |
| 2026-10-11 | v3 | Not yet measured | Not yet measured | Case 6 is the most likely false trigger; the description separates it with "asks for a report" |
