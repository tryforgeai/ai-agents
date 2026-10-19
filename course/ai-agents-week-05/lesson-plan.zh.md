# Week 05 听课速览（2026-10-18）

| 时间 | 内容 | 讲者 | 笔记位置 |
| --- | --- | --- | --- |
| 上午–下午 | **What Did We Miss?**：W3 Lab `when-the-time-is-right` 揭晓（85 页，六幕 + 小测 2–5 + 15 步） | Asif Qamar | notes Part 1 |
| 下午 | **Capstone Project Briefs**（125 页）：6 个项目、四大支柱、W12 提案 → W16 黑客松 | Asif Qamar | notes Part 1b |
| 15:25–17:54 | **Tools Prelude**（29 页）：MCP、工具设计、harness、多 agent 过早扩展、安全五页 | Asif Qamar | notes Part 2 |
| 18:08–19:30 | **The Inference Story**：prefill/decode、KV cache、指标、五种并行、前沿技巧、内存与互连层级 | Sushanth Sivaram Vallath（客座） | notes Part 3 |
| 课后 | FastMCP quickstart + 类型标注实验；FinePrint MCP 原型 | 自己 | lab-log 实验 2；`capstone/fineprint-mcp/` |

## 主线

1. **一行请求，十五步工作**：难的是没说出来的东西 → 补上下文 + 拿原文核对 + 读回校验
2. **工具是模型的手**：模型只读签名和 docstring → 类型、docstring、契约、输出裁剪决定工具好不好用；docstring 也是攻击面
3. **推理是成本的来源**：agent 多轮调用最贵 → 少轮数、短输出、稳定前缀；扩展靠按通信频率叠加的并行

## 小测（Part 1）

Quiz 2–5 的题和我的答案在 notes Part 1；p.77 "Which check catches each?" 六种情况的答案也在那里。

## Lab

- 实验 1：W3 skill 复跑 100/100（只测了"判"，没测"读"）
- 实验 2 / 2b / 2c：FastMCP quickstart；去掉类型 → schema 变 `{}`、结构化输出消失；错误类型有类型时被拦、无类型时静默通过
