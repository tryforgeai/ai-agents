# Permission-Aware Retrieval — Short Version / 精简版

2026-11-15 · Rosso Han · Full version: [English](permission-aware-retrieval.md) · [中文](permission-aware-retrieval.zh.md)

**One line:** enforce permissions with deterministic infrastructure at the moment of retrieval, not by asking the model to behave afterwards.
**一句话：** 权限要在检索的那一刻用确定性的基础设施来执行，而不是在检索之后再请模型自觉遵守。

## English

1. **Authorization is a hard constraint, not a score.** Compute `D_u` first, then search inside it.
   *Why:* as a score term, a relevant enough confidential doc can outweigh missing permission. The better the retriever, the more precisely it leaks.
2. **Prevent, don't suppress.** Unauthorized chunks never enter the context window.
   *Why:* once text is in the prompt, "don't reveal it" is one prompt injection away from the output.
3. **Pre-filter, never post-filter.**
   *Why:* top-10 minus 8 deletions silently becomes top-2.
4. **A normalized security descriptor on every chunk.**
   *Why:* retrieval is per chunk; chunking keeps content but drops permissions; an index cannot filter in five source dialects.
5. **Missing fields deny, deny beats allow, version the descriptor.**
   *Why:* avoid failing open; explicit denies must win; decisions must be replayable.
6. **Sync entitlements by event, not TTL.**
   *Why:* permissions change far more often than content; 10:01 index / 10:05 revoke / 10:06 query = leak window.
7. **Bitmaps under the hood, then search inside the allowed set.**
   *Why:* permission changes need no re-embedding; at 1–10% selectivity the HNSW graph breaks, so partition or use ACORN-style methods and benchmark that zone.
8. **Cover six leakage surfaces:** retrieval, context, answer, citations/metadata, cache, logs.
   *Why:* side channels bypass content filtering; even a refusal can confirm a document exists.

## 中文

1. **授权是检索的硬约束，不是分数。** 先算 `D_u`，再在里面检索。
   *为什么：* 当成分数项，足够相关的机密文档会抵消权限劣势；检索器越准，泄漏越精准。
2. **预防，不要压制。** 未授权 chunk 根本不进上下文。
   *为什么：* 进了 prompt 再让模型"别说"只是请求，离泄漏只差一次 prompt injection。
3. **前置过滤，绝不后置过滤。**
   *为什么：* top-10 删掉 8 条就静默变成 top-2。
4. **每个 chunk 带归一化安全描述符。**
   *为什么：* 检索按 chunk 发生；切片保留内容不保留权限；索引没法同时按五种方言过滤。
5. **缺字段即拒绝，deny 优先，描述符带版本号。**
   *为什么：* 防 fail open；显式否定必须胜出；判定要能回放。
6. **权限同步靠事件推送，不靠 TTL。**
   *为什么：* 权限比内容变得快得多；10:01 / 10:05 / 10:06 的缝隙就是泄漏窗口。
7. **底层是 bitmap，再在允许集合内搜索。**
   *为什么：* 权限变更不用重新 embed；选择率 1–10% 时 HNSW 图会断，要分区或用 ACORN 类算法，并专门测这个区间。
8. **防住六个泄漏面：** 检索、上下文、答案、引用/元数据、缓存、日志。
   *为什么：* 侧路会绕过内容过滤；连拒答本身都可能确认文档存在。
