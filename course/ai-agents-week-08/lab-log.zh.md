# Week 08 Lab Log · The Genie's Bazaar

搭档：
kit：`genies-bazaar/`（OpenRouter，ZDR；student = claude-haiku-5.5，reflector / frontier = claude-opus-5.5）
规则：**跑之前先写预测**（没写下来的预测，事后会记成另一个样子）；保留 `runs/` 里每次的输出；先读指令再看分数

## Worksheet

| 任务 | 我的预测 | Naive | 最佳 arm 和分数 | 缺口：信息 / 知识 / 能力 |
| --- | --- | --- | --- | --- |
| Registry | MIPRO 会很差；GEPA 胜 | 0/30 | **GEPA 30/30**（3 seed 全满分，约 $0.8/seed）；MIPRO 0 | **信息**（API 真实行为） |
| Taxonomy | | | | |
| Library | | | | |
| Gymnasium | | | | |

## Stall 1 · Hostile Registry

**预测**（跑之前填）：
1. naive 便宜 agent 的 test 分数：
2. 强模型 + 同一个 prompt 会好很多吗？为什么：
3. 哪个精灵更强、强多少：
4. 赢家指令里会出现的一句话：

| arm | seeds | dev | test mean | min | max | $ |
| --- | --- | --- | --- | --- | --- | --- |
| none（smoke） | 1 | 0.00（0/12） | 0.00（0/30） | 0.00 | 0.00 | 0.114 |
| none | 3 | 0.00 | **0.00** | 0.00 | 0.00 | 0.34（3×0.114，seed 1、2 命中缓存，1 秒跑完） |
| **gepa** | 3 | **1.00** | **1.00（30/30 ×3）** | 1.00 | 1.00 | **2.37**（0.76 / 0.85 / 0.77） |
| mipro | 3 | 0.00 | **0.00** | 0.00 | 0.00 | 2.75（1.23 / 1.19 / 0.34） |
| none（frontier） | | | | | | （待跑） |

### 正式结果解读（2026-11-08 16:5x）

**1. 结论：GEPA 0 → 30/30，三个 seed 都满分；MIPRO 三个 seed 都是 0，花得还更多**

- 和噪声底比：n=30 时 0 → 1.0 差了 30 题，远超任何浮动，而且 3 个 seed 一致。**这是真提升**
- 三份数据分开：train 18 / dev 12 / test 30，分数来自 test，只碰一次 ✅
- 注意 **none 的 3 个 seed 不独立**：temperature=0 + DSPy 缓存，seed 1、2 直接复用 seed 0 的结果

**2. MIPRO 为什么是 0（印证运行时看到的日志）**

- `Bootstrapped 0 full traces after 17 examples`：naive agent 一题都没对，**没有成功轨迹可当示例**；训练样本里也没有标准答案或轨迹 → 示例那一半完全失效
- 提指令时看不到失败原因，只能写泛泛的指令 → 和种子差不多
- = 手册表 3 的「MIPRO 读分数，GEPA 读句子」；= p.74 左下角「信号少」。**起点 0 分时，只看分数的优化器无从下手**

**3. GEPA 写了什么（Q3：事实 vs 通用建议）**

三个 seed 的 `react.react` 指令都在 4.5k–4.8k 字符（种子约 100 字符，**约 45 倍长**），都学到了全部 5 处：

| 规则 | seed 0 | seed 1 | seed 2 |
| --- | --- | --- | --- |
| 名字 'Last, First'，第一次就用对 | ✅ | ✅ | ✅ |
| 页码从 0 开始，翻到 next_page 为 null | ✅ | ✅ | ✅ |
| since 用 DD-MM-YYYY | ⚠️ **写错了**：「If you use since, give it in ISO YYYY-MM-DD」 | ✅ | ✅ |
| 金额是 paise，refund 参数是卢比 | ✅（标 CRITICAL） | ✅ | ✅ |
| 退款带 idempotency key | ✅ 总是带 | ⚠️「optionally」 | ✅ 总是带 |

- **事实类句子**（这个 API 的真实行为 + 具体例子「120000 paise → refund 1200」）占大部分，**真正起作用的是它们**
- **通用建议**也有：「Read error messages carefully」「Double-check any arithmetic」，属于 intron（不改行为的文字）
- ⚠️ **seed 0 留下了一条错误事实**（since 用 ISO），但同一段又说「翻完所有页自己数最安全」，agent 实际不用 since → **错句没被惩罚，所以活了下来**。这正是 p.7 讲的 intron 风险：test 上满分不代表每句话都对。换一个必须用 since 的任务就会出事
- ⚠️ seed 1 写了「**A first attempt that fails and is then corrected still counts as a mistake**」：GEPA **学到了验证器的脾气**（试错一次也判 0），这是在适应 metric 本身，不是 API。这一句在真实系统里没必要
- 指令里出现了具体客户名（"Kapoor, Nisha"、"Pillai, Leela"…），是从训练反馈里抄来的例子；只当格式示范，不含答案，但说明 GEPA 会把训练样本细节写进 prompt
- seed 2 的 `extract.predict` 没改（69 字符），说明只改 react 那一个就够了

**4. 最佳候选什么时候出现（Q5）**

| seed | 迭代数 | 最终候选 | 首次被选中在第几轮 | merge 次数 |
| --- | --- | --- | --- | --- |
| 0 | 31 | #3 | 第 4 轮 | 3 |
| 1 | 25 | #4 | 第 14 轮 | 4 |
| 2 | 29 | #3 | 第 5 轮 | 3 |

- seed 0、2 在**前 5 轮**就找到最终版本；之后每轮抽到的 3 道题都已全对，GEPA 没有错可读，**剩下的预算基本空转**
- → 预算 150 明显偏多。Try this 2（预算减半）大概率不掉分。只有 seed 1 晚一些（第 14 轮）
- 只产生了 4–5 个候选，货架很小：反馈太好，一两次反思就几乎修完了
- **更正**：之前笔记说「kit 里 GEPA 没开 merge」是错的。`arms.py` 没传 `use_merge`，但 DSPy 3.4.1 的 GEPA **默认开了 merge**，日志里每个 seed 都有 3–4 次 `invoked_merge`

**5. 成本（Q4 的思路）**

- GEPA 每个 seed 约 $0.8，含 opus 反思；MIPRO 花得更多（$1.2）却是 0
- 代价：prompt 从约 100 字符涨到约 4.7k 字符，**每次调用都多付这些 token**。按 1 万次调用算要把这部分加进去（p.82 第 5 条：调用次数少就不划算）。这里收益是 0 → 100%，显然值

**6. 我的预测对了几条**

- ✅ MIPRO 会很差（看到 bootstrap 0 时预测的）
- ✅ GEPA 最容易学到名字格式
- ❌ 「paise 最难学」：三个 seed 全学到了，还标了 CRITICAL。原因可能是退款题的反馈也提到 `remaining` 是 paise，信号比我想的多
- ❓「latest 类会学得慢」：最终都满分，看不出；要看 candidate_tree.html 里中间候选的逐题分数才能验证

环境备注：公司网络做 TLS 检查 → `CERTIFICATE_VERIFY_FAILED`；导出 macOS 钥匙串到 `~/macos-ca-bundle.pem`，设 `SSL_CERT_FILE` / `REQUESTS_CA_BUNDLE` 后 `bazaar doctor` 两个 ready。smoke 有 2 次 max_tokens=2000 截断警告，暂不改。

trace 笔记（每个失败任务：第一个本该学到东西的调用）：

**Trace 1 · total_since**（Leela Pillai，10 March 2026 之后的总额；期望 16120）

| # | 调用 | 返回 | 类型 |
| --- | --- | --- | --- |
| 1 | `find_customer("Leela Pillai")` | error: no customer | 🔊 有报错 |
| 2 | `find_customer("Pillai, Leela")` | C111 | ✅ **自己恢复** |
| 3 | `list_orders(page=1, since="2026-03-10")` | error: since must be DD-MM-YYYY | 🔊 有报错 |
| 4 | `list_orders(page=1, since="10-03-2026")` | 一页订单，amount 25000、340000… | ✅ 日期恢复；❌ **page=1 静默跳过最新 5 单** |
| — | 没翻页，答 **803000** | | ❌ **把 paise 当卢比**（803000 paise = 8030 卢比），只算了一页 |

→ **第一个本该学到东西的调用是 #4**：返回里 amount 是 25000、340000 这种数（订单不可能 3400 卢比 ×100），而且有 `next_page`。agent 没起疑心

**Trace 2 · latest**（Nisha Kapoor 最新订单；期望 ORD-1163）

| # | 调用 | 返回 | 类型 |
| --- | --- | --- | --- |
| 1–2 | 名字先错、再用 "Kapoor, Nisha" | C116 | 🔊 报错 → ✅ 恢复 |
| 3 | `list_orders(page=1)` | 第一个是 ORD-1160 | ❌ **静默**：拿到的是第 6 新的订单 |
| — | 答 ORD-1160 | | ❌ |

**Trace 3 · refund_partial**（Karan Rao 最早的订单退 100 卢比）

| # | 调用 | 返回 | 判断 |
| --- | --- | --- | --- |
| 1–2 | 名字先错、再用 "Rao, Karan" | C122 | 🔊 报错 → ✅ 恢复 |
| 3–4 | `list_orders(page=1)`、`page=2` | 两页订单 | 🔇 跳过了第 0 页；但最早的订单在后面几页，**碰巧没影响** |
| 5 | `get_order(ORD-1221)` | 18-01-2026，amount 45000，refunded 0 | ✅ 找对了最早订单 |
| 6 | `refund(ORD-1221, 100.0)` | ok，refunded_total **10000** | ✅ **退款完全正确**：100 卢比 = 10000 paise |
| 7 | 再查一次 | refunded 10000 | agent 按文档以为单位是卢比 → **误以为多退了 100 倍** |
| 答 | 「**Not done.** …recorded as 10000 instead… units mismatch… needs human review」 | | ❌ 报告错了，但**没有重试**（重试就真的重复退款了） |

**verdict**：0 分，只有两条：名字失败过（已恢复）+ 没读第 0 页。**没有**「账本状态错」，**也没有**「答案错」

→ **这就是 Q4 要找的那种题，而且更极端**：

1. **账本状态是对的**（ORD-1221 刚好多退了 10000 paise，和期望一致），最后却是 0 分。原因是 `verify` 只要有任何一条 note 就判 0，而「名字先试错一次」也算一条，**即使已经恢复**。也就是说：这个验证器要求 agent **第一次就用对名字格式**，过程分和结果分是绑在一起的
2. **metric 被字面读了**：答案是「**Not** done」，但 `_matches` 只检查 `"done" in answer.lower()`，所以**判为答案正确**。这正是 W7 p.97 Doors A 的「the metric, read literally」：一个本该算错的回答，靠子串碰巧过关
3. **静默的单位错误让 agent 制造了假警报**：它把正确的退款当成错误，还建议人工回滚 9900。放到真实系统里，这会让人去撤销一笔正确的退款。好的一面：它**停手并上报**，没有自己再动账本

**Q1 答案（初稿）**：**会报错的不一致（名字格式、日期格式）agent 都自己恢复了；静默的不一致（页码从 0 开始、单位是 paise）它从来没发现。** 共同点：恢复与否取决于 API **有没有开口说话**，跟错误本身难不难无关

**⚠️ 发现：反馈句会误导 GEPA**

- Trace 2 的反馈只有两句：「答案错」+「find_customer failed: … 'Last, First'」。可名字问题 agent **已经恢复了**，不是失败原因；**真正的原因（page 从 0 开始）一句没提**
- 源码原因：`tasks.py: verify` 里页码那条提示写了 `task.kind != "latest"`，`latest` 类被排除了
- Trace 1 也一样：反馈把 4 条已恢复 / 未恢复的问题**混在一起列**，没区分「真正导致错误的」和「绕了弯但修好了的」
- → 这就是手册表 3 里 GEPA 的风险「**feedback that points the wrong way**」的真实样本。预测：GEPA 在 `latest` 类上进步会比 `total/count` 慢（看 GEPA 指令里页码规则是不是靠别的题型学到的）

赢家指令摘录（事实 / 通用建议分开标）：

Q1–Q6：

## Stall 2 · House Taxonomy

**我猜的规则**（读 30 条便签后写，写完前别打开 taxonomy.py）：

**预测**：naive 准确率＿；frontier-fewshot 能补上差距吗＿；哪个精灵赢＿

| arm | seeds | dev | test mean | min | max | $ |
| --- | --- | --- | --- | --- | --- | --- |
| none | | | | | | |
| fewshot | | | | | | |
| frontier-fewshot | | | | | | |
| gepa | | | | | | |
| mipro | | | | | | |

错误模式：

Q1–Q5：

## Door A · Library

**预测**：闭卷曲线形状＿；frontier-closed 的位置＿；small-rag vs frontier-closed＿；GEPA 的增量＿

| arm | test | $ | rarest | rare | middle | known | famous |
| --- | --- | --- | --- | --- | --- | --- | --- |
| small-closed | | | | | | | |
| frontier-closed | | | | | | | |
| small-rag | | | | | | | |
| small-rag-gepa | | | | | | | |
| 天花板 answer_in_lead | — | — | 0.875 | 0.95 | 0.95 | 0.95 | 0.85 |

5 道错题归因（记忆 / 检索 / 阅读）：

## Door B · Gymnasium

手解 3 题（计时）：

**预测**：naive 准确率＿；精灵能到＿；RL 能到＿，曲线形状＿；答案长度变化＿

| 方法 | well-formed | correct | $ / 小时 |
| --- | --- | --- | --- |
| zero-shot | | | |
| gepa | | | |
| mipro | | | |
| GRPO checkpoint | | | |

## 下课前五问

1.
2.
3.
4.
5.
