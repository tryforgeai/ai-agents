# Week 07 学习总结（2026-11-01 课 · 课后版）

> 逐页细节：[notes.zh.md](notes.zh.md) · 动手记录：[lab-log.zh.md](lab-log.zh.md) · 讲义精读：[lesson-plan-精读.zh.md](lesson-plan-精读.zh.md)
> 已覆盖：上午白板 + Orientation（deck p.2–33）、下午 Workshop / Genie's Exam、17:00 客座讲座、晚上 Deep Dive D1–D3（p.47–60）。p.60 之后（D4 纪律、field notes 兑现、优化器配 artifact、综合）和 Owl 五行没有截图，待看录播补。

## 一句话

**A prompt is a parameter — a point in a discrete space with no gradient — and prompt optimization is search over that space, steered by a pseudo-gradient written in words. The optimizer is only ever as good as the metric it is handed.**

板书版：**θ\* = argmax_θ E_(x,y)~D [ µ(Φ(x;θ), y) ]**，权重冻结，只能重新调配模型已有的行为，装不进新本事。

---

## 1. 核心概念

| 概念 | 一句话 | 我在哪里亲手碰到 |
| --- | --- | --- |
| **prompt 是参数** | θ = (π 指令, δ 示例)；ŷ = Φ(x; θ)，µ(ŷ, y) 打分 | 白板 x → ŷ → y |
| **三个诅咒** | 离散巨大（10¹⁸⁸）→ 没梯度；有噪声（n=50 时 ±6.5 点）→ 不能「高了就留」；昂贵（一次打分 = n 次运行） | Bench 2 每版都要读 12 行 |
| **伪梯度** | 没有坡度，方向要人造；六家：运气 / 建议 / 批评 / 变异选择 / 预测 / 积累；最丰富的是「模型读自己的失败」 | Bench 4 B 轮 |
| **µ_f 反馈函数** | 除了分数，还要一份文字记录（错在哪、为什么）；**GEPA 最重要的杠杆** | Bench 4 的 why 句子 = 手写 µ_f |
| **instance frontier** | 前沿坐标是**每道题**，不是「清晰 × 简洁」这类目标；某题最好就保留 | Bench 7：B 赢 #15、C 赢 #17 |
| **两个数据池 + holdout** | feedback（被读过）· pareto（被选过）· holdout（只考一次） | Bench 2 只有 feedback；Bench 10 是 holdout |
| **metric 照字面读** | Goodhart + 搜索引擎；loss 塌缩、intron 都是同一种漏洞 | Genie's Exam A1 |
| **tether** | 关键规则钉死不可改（文本版 KL，硬约束） | Field notes 第 4 课 |
| **judge 需要 rubric** | 无 rubric 46.4%（硬币），有 rubric 73.8% | Bench 9 |
| **何时不优化** | 72 次运行 49% 比 zero-shot 差；只有「模型能但不做」时才有用 → 先做 headroom test | Headline 6、Bench 1 |

## 2. GEPA 的循环

**准备（一次）**：人写初稿 + 三份数据 + 会说话的 metric + 预算 → 种子在 Pareto 集上打分

**循环（重复到预算用完）**：① 按赢题数选父代 → ② 轮流选模块 → ③ 小批量跑 + 收 µ_f → ④ 反思改写（或合并）→ ⑤ 小闸门：必须赢父代 → ⑥ Pareto 集逐题打分 → ⑦ 剪掉逐题被支配的

**收尾（一次）**：选聚合分最高 → holdout 只考一次（多 seed、分 slice）→ 人工删 intron

外面还套着一层人的循环：人写初稿 → GEPA 改 → 人再改 → 跑 eval → 再来。

**Proposer + Judge**（p.51）：Workshop = 提议者（写 why、小步、记住失败、保留专家、合并），Genie's Exam = 裁判（metric、数据、tether），GEPA = 两者组成的循环。

已整理成可分享的英文文档：[GEPA: How Reflective Prompt Optimization Works](https://claude.ai/artifact/6Ny8LQz754796x1jmM65bT)

## 3. Field notes 四课（贯穿全天的合规项目故事）

1. **先拆开**：不是能力缺口，是 **resolution gap**，几十种风险压在一个 prompt 里
2. **苦活是数据**：one blessed goldset、one owner、every change logged；一条坏例子会被忠实地学成规则
3. **思考是 metric**：每种风险一个 F_β 旋钮（严重风险偏召回）；定义「好」才是真正的设计工作
4. **保险是 tether**：校准规则和风险定义钉死 → 结局：系统解释好到客户拿来培训新员工

## 4. 工作台的真名（D1 揭晓）

| Bench | 名字 | Bench | 名字 |
| --- | --- | --- | --- |
| 1 | headroom test（第 0 步） | 6 | rejected-edit buffer |
| 2 | resolution gap | 7 | instance-level Pareto frontier |
| 3 | noisy objective | 8 | system-aware merge |
| 4 | reflective mutation / µ_f | 9 | judge pathologies |
| 5 | bounded edit budget | 10 | held-out set |
| 11 | GEPA itself | | |

> *"Every bench was one move an optimizer makes. Bench 1 is the one it should make first."*

## 5. 我做了什么、学到什么

| 练习 | 结果 | 学到的 |
| --- | --- | --- |
| Bench 2 | v1→v5，12 条中 11 条达标；v1 照装箱单放款 $1,150 → v5 改成 CHECK | 先分类再改；每轮可能修一处坏一处；例子别用考题；规则冲突时删掉冲突的那句 |
| Bench 4 | A 轮凭感觉 3 版停在 4/6；B 轮写 why 4 版到 6/6 | 写下「为什么」才能抓到细问题（编造承诺）；规则太绝对会矫枉过正 |
| Bench 7 | A/B/C 各有一招 → v1 合并丢了「只用卡片」被拒 → v2 七题全拿星 | 按题保留专家；合并时最容易丢旧规则；这就是 GEPA 的一轮 |
| Genie's Exam A1 | 0.96 分但删光关键信息；只有 p3「按关键事实打分」1 轮修好 | 改考试比改精灵有效；会说话的 metric 学得快 |

## 6. 客座讲座：AI 训练的网络（Rip Sohan）

- **问题**：算力涨 1000×、带宽只涨 10×；同步训练 → **尾延迟**（最慢的包卡住全集群）+ **incast**（多对一冲爆缓冲区）
- **以太网的四根支柱**：包喷洒（每个包走多条路）→ 乱序直写（包带内存地址标签）→ 选择性重传（SACK 只补缺口）→ 拥塞控制（NSCC 发送方 + RCCC 接收方额度）+ **包修剪**（丢数据不丢消息）
- **标准**：Ultra Ethernet（UEC）、MRC（OCP，Multipath Reliable Connection）、MetaRoCE（Meta）、Falcon（Google）
- **vs InfiniBand**：都是 RDMA、传输层都在网卡；IB 靠「网络绝不丢包」，以太网方案靠「丢了也能快速精确补回」；IB 封闭成熟（基本 NVIDIA 一家），以太网开放
- **市场**：Dell'Oro 数据，AI 后端网络交换机 2023 年 IB 占近 80% → 2025 年以太网反超 → 2026 Q1 以太网约占三分之二
- **DeepSeek 对照**：在 H800 + InfiniBand 上从**软件层**省网络（每 token 最多 4 个节点、同节点只跨网一次再走 NVLink、FP8 通信、不用张量并行、DeepEP）；讲座从**网卡和协议层**把剩下的流量送好，两者叠加

## 7. 记号提醒

白板上 θ\* 是权重、Φ 是 system prompt；讲义和 D2 里 **θ = (π, δ) 是 prompt、Φ 是程序**。复习以讲义为准。

## 8. 待办

- [ ] 看录播补 p.60 之后：D4 纪律、field notes 兑现、优化器配 artifact、综合、**Owl 五行**（填进精读笔记）
- [ ] Bench 9 做完镜子环节；Bench 10 Sea Trial 用 Bench 2 的 v5（等讲师 code）
- [ ] Genie's Exam：A3、B1、C1（周二 / 周四 session）
- [ ] 下载 workshop notebook 和 exam field notes 放进 `uploads/`
- [ ] 拿到 Reservoir PDF，读 §1、§3、§4、§5、§12
- [ ] 必读论文精读：GEPA（§2–3）、DSPy、ACE、SkillOpt
- [ ] 周二 / 周四：跑 `dspy.GEPA` 代码
- [ ] 下周 Week 8：Memory（ACE 的 context collapse 是引子）
