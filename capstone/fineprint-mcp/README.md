# FinePrint MCP — 我的第一个 MCP 工具集（capstone 原型）

一个**合成数据**的小商店，用 FastMCP 暴露成 4 个 MCP 工具，配一个独立校验器。
规则来自通用的公开电商政策（`rules.md`），**没有 cash-back**，不含任何雇主数据。

## 文件

| 文件 | 作用 | 对应技巧 |
| --- | --- | --- |
| `rules.md` / `rules.json` | 大白话规则 + 编号；JSON 存数字 | 规则先写、代码执行 |
| `fineprint/store.py` | SQLite + 确定性种子数据；`FINEPRINT_TODAY` 固定"今天" | 可复现 |
| `fineprint/decide.py` | **纯函数**：报价、退换货判定；无 I/O、无 LLM | 原则 1、封闭结果、notes |
| `fineprint/server.py` | 4 个 `@mcp.tool`：强类型、docstring 写"何时不用"、前置/后置检查、来源+时间戳 | p.14–17、#25、#47、#48 |
| `verify.py` | **独立校验器**：只读数据库和 rules.json，不 import fineprint；算 RLVR 奖励 | #49 |
| `tasks/*.json` | 任务：顾客目标 + 唯一正确的终态 | FinePrint 提案 |
| `client_demo.py` | 通过 HTTP 走一遍 R-117 | — |
| `try_cases.py` | 11 个边界用例打到运行中的 server，自动 PASS/FAIL；只读，可反复跑 | — |
| `tests/` | 30 个测试：规则逐条、MCP 层契约、端到端、校验器独立性 | — |

## 4 个工具

| 工具 | 类型 | 说明 |
| --- | --- | --- |
| `get_order(order_id)` | 观察 | 订单、送达天数、每行实付、是否已退 |
| `list_coupons(customer_id)` | 观察 | 优惠券及今天能否用、积分余额 |
| `quote_cart(customer_id, items, coupon_codes, points)` | 观察（纯计算） | `ok` / `rejected` + 每条违规的规则编号 |
| `request_return(order_id, sku, kind, new_sku, confirm)` | **动作** | `confirm=False` 只出预览；`confirm=True` 才写库。结果是封闭清单：`preview / done / already / final_sale / outside_window / invalid_exchange / out_of_stock` |

## 在 Mac 上运行

```bash
cd "<这个文件夹>"
python3 -m venv .venv && source .venv/bin/activate
python3 -m pip install -r requirements.txt

python3 -m pytest -q                      # 30 passed

python3 -m fineprint.store                # 重置商店数据
python3 -m fineprint.server --http        # 终端 1：启动在 http://127.0.0.1:8000/mcp
python3 client_demo.py                    # 终端 2：走一遍 R-117
python3 verify.py tasks/R-117.json        # 独立校验终态 → reward 1.0
python3 try_cases.py                      # 11/11 as expected
```

每个任务跑之前先 `python3 -m fineprint.store` 重置，否则上一个任务写入的退货会让下一个任务的"没有多余退货"检查失败。

`quote_cart` 被拒时 `total_cents` 等金额为 `null`（只保留 `subtotal_cents`），避免模型把一个店铺不接受的价格念给顾客。

端口被占（`Errno 48`）时：`lsof -ti :8000 | xargs kill`。

## 下一步
- 加更多任务（目标 150 训练 / 60 测试），每个任务用 decide 层确认"恰好一个正确终态"
- 记录 run log（每次工具调用、TTFT、token 数）
- 接 DSPy agent 和 GRPO：`verify.verify()` 直接当 reward 函数
