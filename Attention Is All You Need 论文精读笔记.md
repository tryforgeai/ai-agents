# Attention Is All You Need 论文精读笔记

> **Attention Is All You Need**
> Ashish Vaswani\*, Noam Shazeer\*, Niki Parmar\*, Jakob Uszkoreit\*, Llion Jones\*, Aidan N. Gomez\*, Łukasz Kaiser\*, Illia Polosukhin\*（\* 全部同等贡献，**作者顺序随机**）
> Google Brain · Google Research · University of Toronto
> NIPS 2017 · arXiv:1706.03762**v7**（2023-08-02 版）
> 原文 PDF：`Projects/LLM and Enterprise RAG Bootcamp/course/week_04/chunking_pipeline/data/attention.pdf`
> 代码：tensor2tensor（https://github.com/tensorflow/tensor2tensor）

> ⚠️ 本笔记基于 **v7**。arXiv 上各版本的数字有过改动（见 §7.1），引用时注明版本。

---

## 0. 一句话总括

**把 encoder-decoder 翻译模型里的 RNN 和 CNN 整个拿掉，只留 attention + 逐位置的 FFN + 残差/LayerNorm，在 8 张 P100 上训 12 小时就拿到 WMT14 英德的新 SOTA；它真正的意义是让序列建模变成了能完全并行的矩阵乘法。**

核心贡献不是 attention（那是 Bahdanau 2014 [2]），也不是 self-attention（Cheng 2016、Parikh 2016、Lin 2017 都已经在用），而是：

> **证明了「只靠 attention、完全不要循环」的模型能做 transduction，并且给出了一套至今基本没变的工程配方：scaled dot-product、multi-head、正弦位置编码、warmup 学习率。**

⚠️ **评测本身限定了论文能主张什么：**

1. **只有 BLEU，没有人工评测，没有方差。** 所有结果都是单次运行，没有 seed、没有置信区间。消融（Table 3）里很多差距只有 **0.1–0.3 BLEU**，这些差距可能就是噪声。→ 论文能主张「Transformer 在**同等或更低训练成本**下达到或超过 SOTA」，**不能**主张 Table 3 里每一行的排序都是真实的。
2. **任务是句子级翻译，序列很短。** 「self-attention 比 RNN 便宜」的论证**明确依赖 n < d**（§4）。→ 论文能主张它适合**当年的句子级任务**，对长序列它自己也承认需要 restricted attention（§4 结尾）。今天的长上下文场景正好落在它论证的反面。

---

## 1. 动机与定位

### 1.1 摘要里的主张，顺序有讲究

摘要列的优点按顺序是：

1. **superior in quality**（质量更好）
2. **more parallelizable**（更容易并行）
3. **significantly less time to train**（训练时间短得多）
4. **generalizes well to other tasks**（迁移到句法分析）

🔑 让它被整个领域接受的是**第 2 条**，不是第 1 条。BLEU 只比 ensemble 高 **2.04**（28.4 − 26.36），但「训练没有时间维度上的串行依赖」这件事，后来让模型能扩到几十亿、几千亿参数。BERT、GPT 用的都是这一条。论文自己对此有自觉：

> *"This inherently sequential nature precludes parallelization within training examples, which becomes critical at longer sequence lengths"* —— §1 Introduction

### 1.2 当时的三条路线

| 路线 | 代表 | 远距离两点之间要走几步 | 问题 |
| --- | --- | --- | --- |
| RNN / LSTM + attention | GNMT [38] | **O(n)** 串行步 | 训练时没法在序列内并行 |
| CNN | ByteNet [18]（**O(log n)**）、ConvS2S [9]（**O(n)** 线性） | 随距离增长 | 远距离依赖难学 |
| **纯 attention** | **Transformer** | **O(1)** | 代价是「平均化导致分辨率下降」，用 multi-head 补 |

> *"In the Transformer this is reduced to a constant number of operations, albeit at the cost of reduced effective resolution due to averaging attention-weighted positions"* —— §2 Background

🔑 这句话是全文唯一一处主动承认架构代价的地方，而且直接引出了 multi-head 存在的理由（§2.3）。

🔑 评测要和用途匹配：这是一篇**翻译论文**，标准是 BLEU 和训练成本。用「长上下文」「推理能力」去批它不公平；但用「它关于复杂度的论证有前提条件」去批是公平的，见 §10.2。

---

## 2. 方法精读（§3）

### 2.1 整体结构（Figure 1）

```
输入 token → Embedding × √d_model + 正弦 PE → dropout
  → Encoder × N=6:  [Multi-Head Self-Attn → Add&Norm] → [FFN → Add&Norm]
输出 token（右移一位）→ Embedding × √d_model + PE → dropout
  → Decoder × N=6:  [Masked Self-Attn → Add&Norm] → [Enc-Dec Attn → Add&Norm] → [FFN → Add&Norm]
  → Linear（与 embedding 共享权重）→ Softmax
```

- **N = 6**（encoder 和 decoder 各 6 层）
- 所有子层和 embedding 的输出维度都是 **d_model = 512**，为了让残差能直接相加
- 子层输出：**LayerNorm(x + Sublayer(x))**，即 **Post-LN**

🔑 Post-LN 是原论文的写法，现在的 LLM 几乎都改成了 **Pre-LN**（`x + Sublayer(LayerNorm(x))`），后来还换成了 RMSNorm。后来的研究（Xiong et al. 2020，**课外补充**）指出 Post-LN 在训练初期梯度不稳定，**这很可能就是 §5.3 里非要 warmup 的原因**。论文本身没有讨论这一点。

### 2.2 Scaled Dot-Product Attention（§3.2.1）

$$\text{Attention}(Q,K,V) = \text{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right)V$$

- 和普通点积 attention 的**唯一区别**就是除以 **√d_k**（base 模型 d_k = **64**，所以就是除以 **8**）
- 为什么要缩放，见脚注 4：如果 q、k 的各分量独立、均值 0、方差 1，那么 q·k 的**均值是 0，方差是 d_k**。d_k 越大，点积的数值越大，softmax 就越饱和，梯度会变得极小

> *"We suspect that for large values of d_k, the dot products grow large in magnitude, pushing the softmax function into regions where it has extremely small gradients"* —— §3.2.1

⚠️ 原文用的是 **"We suspect"**（我们猜测）。缩放的理由是**假设**，不是被证明的结论；论文也没有做「不缩放」的消融。

- 为什么选点积而不是加性 attention：两者理论复杂度相近，但点积能直接用**高度优化的矩阵乘法**。论文也承认，d_k 大的时候，**不缩放的点积 attention 效果不如加性 attention** [3]。

🔑 选点积的理由是**硬件**，不是建模能力。这一点决定了后来整个推理系统都围着 GEMM 和 KV cache 优化（↔ §9.1）。

### 2.3 Multi-Head Attention（§3.2.2）

$$\text{MultiHead}(Q,K,V) = \text{Concat}(\text{head}_1,\dots,\text{head}_h)W^O,\quad \text{head}_i = \text{Attention}(QW_i^Q, KW_i^K, VW_i^V)$$

- **h = 8** 个头，每个头 **d_k = d_v = d_model / h = 64**
- 每个头的维度都缩小了，所以**总计算量和满维度的单头差不多**
- 投影矩阵：W_i^Q, W_i^K ∈ ℝ^{d_model×d_k}，W_i^V ∈ ℝ^{d_model×d_v}，W^O ∈ ℝ^{h·d_v×d_model}

> *"Multi-head attention allows the model to jointly attend to information from different representation subspaces at different positions. With a single attention head, averaging inhibits this."* —— §3.2.2

🔑 单个头的 softmax 输出是**一个**加权平均，只能代表「一种」关注方式。多个头让同一个位置能同时取到句法上的、指代上的、局部的信息（附录 Figure 4、5 就是例子）。Table 3 (A) 里单头比最好的配置差 **0.9 BLEU**，这是论文给 multi-head 的**唯一**定量证据（§5.1）。

### 2.4 Attention 在模型里的三种用法（§3.2.3）

| 位置 | Q 来自 | K、V 来自 | 遮罩 |
| --- | --- | --- | --- |
| Encoder self-attention | encoder 上一层 | encoder 上一层 | 无（双向） |
| Decoder masked self-attention | decoder 上一层 | decoder 上一层 | **因果遮罩**：未来位置设为 **−∞** |
| Encoder-decoder attention | decoder 上一层 | **encoder 最终输出** | 无 |

- 因果遮罩加上「输出 embedding 右移一位」，保证位置 i 的预测**只依赖 < i 的已知输出**

⭐ **论文没提 padding mask。** §3.2.3 只写了因果遮罩。但附录的可视化里句子后面跟着 `<pad>`（Figure 3 有 **6** 个），而 attention 线一条都没有连到 `<pad>` 上。所以实现里一定有 key padding mask，只是正文没写。手写 Transformer 的人在这里最容易出 bug。

### 2.5 Position-wise FFN（§3.3）

$$\text{FFN}(x) = \max(0,\, xW_1 + b_1)W_2 + b_2$$

- 输入/输出 **d_model = 512**，中间层 **d_ff = 2048**（**4 倍**）
- 每个位置**单独、相同**地计算；不同层参数不同
- 论文的另一种说法：两个 **kernel size = 1** 的卷积

🔑 我算的：每层 attention 的参数约 4·d² ≈ **1.05M**，FFN 约 2·d·d_ff ≈ **2.10M**。**FFN 占每层非 embedding 参数的约 2/3**，论文却只用了一小段来讲它。Table 3 (C) 也显示加宽 FFN 比加宽 d_model 更划算（⭐ §5.2）。后来的 MoE、SwiGLU 改的都是这一块。

### 2.6 Embedding 与 Softmax（§3.4）

- **三处共享同一个权重矩阵**：encoder embedding、decoder embedding、输出前的 linear（参考 Press & Wolf [30]）
- 在 embedding 层里，权重**乘以 √d_model**（512 时约 **22.6**）

⚠️ 三处共享要求源语言和目标语言**用同一个词表**。英德用的是**共享**的 BPE（约 **37000**），说得通；英法用的是 **32000** word-piece，论文没说是否也共享。

🔑 乘 √d_model 的用意论文没有解释。一个常见的解读（**我的推断**）是：共享权重初始化得比较小，乘上它之后，embedding 的量级才不会被加上去的 PE（取值在 [−1, 1]）盖过去。

### 2.7 正弦位置编码（§3.5）

$$PE_{(pos,2i)} = \sin\left(pos / 10000^{2i/d_{model}}\right),\quad PE_{(pos,2i+1)} = \cos\left(pos / 10000^{2i/d_{model}}\right)$$

- 波长从 **2π** 到 **10000·2π** 呈几何级数
- 选择的理由：对任意固定偏移 k，PE_{pos+k} 都能表示成 PE_pos 的**线性函数**，作者**假设**这样模型容易学到相对位置
- 学习式位置编码的结果「几乎一样」（Table 3 (E)：**25.7** vs **25.8** BLEU）
- 最终选正弦的理由：

> *"We chose the sinusoidal version because it may allow the model to extrapolate to sequence lengths longer than the ones encountered during training."* —— §3.5

⚠️ **"may allow"**，而且全文**没有任何外推实验**。这是一个没被验证的假设。后来 ALiBi（Press et al. 2021，**课外补充**）的实验表明正弦编码**外推效果很差**。现代 LLM 主流用的是 **RoPE**，它其实可以看作把「相对位置可以用线性变换表示」这个想法真正做进了 attention 的内积里。

### 2.8 训练配方（§5）

| 项 | 值 |
| --- | --- |
| 数据 | 英德 **4.5M** 句对，BPE 约 **37000**（共享）；英法 **36M** 句，**32000** word-piece |
| Batch | 按长度分桶，每个 batch 约 **25000** 源 token + **25000** 目标 token |
| 硬件 | **1** 台机器，**8 × P100** |
| base | 每步约 **0.4 s**，**100K** 步 ≈ **12 h** |
| big | 每步 **1.0 s**，**300K** 步 ≈ **3.5 天** |
| Adam | β1 = **0.9**，β2 = **0.98**，ε = **10⁻⁹** |
| Warmup | **4000** 步 |
| Dropout | base **0.1**；big（英德）**0.3**；big（英法）**0.1** |
| Label smoothing | ε_ls = **0.1** |

学习率公式：

$$lrate = d_{model}^{-0.5}\cdot\min\left(step^{-0.5},\; step\cdot warmup^{-1.5}\right)$$

🔑 我算的：峰值出现在第 4000 步，base 的峰值约 **7.0 × 10⁻⁴**，big（d_model = 1024）约 **4.9 × 10⁻⁴**。d_model 越大，峰值学习率越小，这是公式里内置的规则。

⚠️ 小出入：0.4 s × 100K = **11.1 h**，论文写 12 h，FLOPs 估算也按 12 h 算。差别不大，但说明「12 小时」是一个取整后的数。

**Label smoothing 的代价**，论文自己说了：

> *"This hurts perplexity, as the model learns to be more unsure, but improves accuracy and BLEU score."* —— §5.4

### 2.9 解码配置（§6.1）

- **Checkpoint averaging**：base 取最后 **5** 个 checkpoint（每 **10 分钟**存一个）；big 取最后 **20** 个
- Beam size **4**，length penalty **α = 0.6**
- 最大输出长度：**输入长度 + 50**
- 句法分析：最大输出长度 **输入长度 + 300**，beam **21**，**α = 0.3**

🔑 Checkpoint averaging 是一个很少有人记得、但对最终分数有贡献的技巧。Table 3 的消融**没有做 averaging**，所以消融的数字和 Table 2 的数字不能直接比（见 ⭐ §4.3）。

---

## 3. 为什么用 Self-Attention（§4）

### 3.1 Table 1

| 层类型 | 每层复杂度 | 串行操作数 | 最长路径 |
| --- | --- | --- | --- |
| Self-Attention | **O(n²·d)** | **O(1)** | **O(1)** |
| Recurrent | O(n·d²) | O(n) | O(n) |
| Convolutional | O(k·n·d²) | O(1) | O(log_k n) |
| Self-Attention (restricted) | O(r·n·d) | O(1) | O(n/r) |

三个比较标准：**每层计算量**、**可并行程度**（最少串行步数）、**远距离依赖的路径长度**。

### 3.2 关键前提：n < d

> *"self-attention layers are faster than recurrent layers when the sequence length n is smaller than the representation dimensionality d, which is most often the case with sentence representations"* —— §4

🔑 n²d 和 nd² 相等的点就是 **n = d**。base 的 d = **512**，所以论文的复杂度优势**只在句子长度小于 512 个 token 时成立**。今天的 128K 上下文配 d ≈ 4096–8192，n/d 在 **16–32** 倍左右，正好落在这个论证不成立的区间。现在长上下文的大部分工程（FlashAttention、滑动窗口、稀疏 attention、线性 attention）都是在处理这个 n² 带来的问题。

论文已经提出了 restricted attention（邻域大小 r）作为长序列的方案，**这就是后来的 sliding-window attention**（Longformer、Mistral）。作者写了 *"We plan to investigate this approach further in future work."*

### 3.3 可解释性

> *"As side benefit, self-attention could yield more interpretable models."* —— §4

⚠️ 是 **"could"**，证据只有附录里挑出来的 3 张图。后来 *Attention is not Explanation*（Jain & Wallace 2019，**课外补充**）专门质疑了「attention 权重 = 解释」这一点。

---

## 4. 实验一：机器翻译（§6.1，Table 2）

### 4.1 主结果

| 模型 | EN-DE BLEU | EN-FR BLEU | 训练 FLOPs（EN-DE / EN-FR） |
| --- | --- | --- | --- |
| GNMT + RL | 24.6 | 39.92 | 2.3e19 / 1.4e20 |
| ConvS2S | 25.16 | 40.46 | 9.6e18 / 1.5e20 |
| MoE | 26.03 | 40.56 | 2.0e19 / 1.2e20 |
| ConvS2S Ensemble | **26.36** | **41.29** | 7.7e19 / 1.2e21 |
| **Transformer (base)** | **27.3** | 38.1 | **3.3e18** |
| **Transformer (big)** | **28.4** | **41.8** | **2.3e19** |

- 英德：big 比之前最好的结果（ConvS2S Ensemble 26.36）高 **2.04**；**base 也已经超过所有前作，包括 ensemble**
- 英法：big **41.8**，超过所有单模型，比 ConvS2S Ensemble 高 **0.51**；训练成本**不到之前 SOTA 的 1/4**（我算的：2.3e19 / 1.2e20 ≈ **0.19**）

### 4.2 作者没报的那部分

- **base 在英法上是 38.1，比 GNMT、ConvS2S、MoE 的单模型都低。** 引言里说「训练 12 小时就能拿到新 SOTA」，这句话只对英德成立（⚠️ §5.1）
- **FLOPs 不是实测值。** 脚注 5：训练时间 × GPU 数 × 每张卡估计的持续单精度算力（P100 取 **9.5** TFLOPS，K80 **2.8**，K40 **3.7**，M40 **6.0**）。我验算了：12 h × 8 × 9.5e12 ≈ **3.28e18** ✓；3.5 天 × 8 × 9.5e12 ≈ **2.30e19** ✓。这是一个上界式的估算，实际利用率不可能是 100%
- **没有方差、没有显著性检验、没有人工评测**

⭐ **Table 2 里 Transformer 的 FLOPs，英德和英法是同一个合并单元格。** 英法数据量是英德的 **8 倍**（36M vs 4.5M），但论文没有单独给英法的训练步数和时间。合并单元格**暗示**两者训练成本一样，那么英法模型在数据上走的 epoch 数要少得多。

### 4.3 ⭐ big 模型的提升里混了 checkpoint averaging

- 开发集（Table 3，**不做** averaging）：big **26.4** vs base **25.8**，提升 **+0.6**
- 测试集（Table 2，**做** averaging）：big **28.4** vs base **27.3**，提升 **+1.1**
- big 平均了 **20** 个 checkpoint，base 只平均了 **5** 个

🔑 两边用的数据集不同（newstest2013 vs newstest2014），所以不能直接相减；但「big 的提升在测试集上几乎翻倍」，**有一部分可能来自 averaging 的窗口更大**，论文没有把这两个因素分开。

---

## 5. 实验二：模型变体（§6.2，Table 3）🔥

所有数字都是**英德开发集 newstest2013**，**不做** checkpoint averaging。PPL 是**按 word-piece 计算**的，不能和按词计算的 PPL 比。

### 5.1 逐行拆

**(A) 头数（总计算量不变）**

| h | d_k = d_v | PPL | BLEU |
| --- | --- | --- | --- |
| **1** | 512 | 5.29 | **24.9** |
| 4 | 128 | 5.00 | 25.5 |
| **8（base）** | 64 | 4.92 | **25.8** |
| 16 | 32 | **4.91** | **25.8** |
| 32 | 16 | 5.01 | 25.4 |

→ 单头差 **0.9**；头太多也会变差。16 头的 PPL 其实**略好于** 8 头。

**(B) 只缩小 d_k**：d_k = **16** → **25.1**（参数 **58M**）；d_k = **32** → **25.4**（**60M**）

> *"This suggests that determining compatibility is not easy and that a more sophisticated compatibility function than dot product may be beneficial."* —— §6.2

**(C) 模型大小**

| 改动 | PPL | BLEU | 参数 |
| --- | --- | --- | --- |
| N = **2** | 6.11 | **23.7** | 36M |
| N = 4 | 5.19 | 25.3 | 50M |
| N = **8** | **4.88** | **25.5** | 80M |
| d_model = 256 | 5.75 | 24.5 | 28M |
| d_model = **1024** | 4.66 | **26.0** | **168M** |
| d_ff = 1024 | 5.12 | 25.4 | 53M |
| d_ff = **4096** | 4.75 | **26.2** | **90M** |

**(D) 正则化**

| 改动 | PPL | BLEU |
| --- | --- | --- |
| P_drop = **0.0** | 5.77 | **24.6** |
| P_drop = 0.2 | 4.95 | 25.5 |
| ε_ls = **0.0** | **4.67** | 25.3 |
| ε_ls = 0.2 | 5.47 | 25.7 |

**(E)** 学习式位置编码：PPL **4.92**，BLEU **25.7**

**big**：N = 6，d_model = **1024**，d_ff = **4096**，h = **16**，P_drop = **0.3**，**300K** 步 → PPL **4.33**，BLEU **26.4**，**213M** 参数。base 是 **65M**。

### 5.2 ⭐ 表里能挖出来、但正文没说的

1. **⭐ 加宽 FFN 比加宽 d_model 更划算**（Table 3 (C)）。d_ff = 4096 只用了 **90M** 参数就到了 **26.2**；d_model = 1024 用了 **168M** 参数才到 **26.0**。参数少了将近一半，BLEU 反而更高。正文只总结了一句 *"bigger models are better"*。
2. **⭐ PPL 和 BLEU 的排序经常不一致**（Table 3 (C)(D)）。N = 8 的 PPL（**4.88**）比 base 好，BLEU（**25.5**）却比 base 差；去掉 label smoothing 后 PPL 是全表第二好的 **4.67**，BLEU 却掉到 **25.3**。🔑 这说明在**单次运行**下，**±0.3 BLEU** 的差距大概率在噪声范围内，表里很多行的排序不能当真。
3. **⭐ 不用 dropout 掉得最多**（**−1.2** BLEU，到 24.6），比单头（−0.9）还多。按这张表，dropout 是 base 模型里**最重要的单个组件**，比 multi-head 还重要。
4. **⭐ 深度：2 层掉 2.1 BLEU，8 层反而不如 6 层。** 在这个数据规模下，加深的收益在 6 层左右就没了（同样受上一条噪声的影响）。

---

## 6. 实验三：英语句法分析（§6.3，Table 4）

- 设置：**4 层**，d_model = **1024**；WSJ 约 **40K** 句（词表 **16K**）；半监督约 **17M** 句（词表 **32K**）
- 只调了 dropout、学习率和 beam，**其它全部沿用英德 base 的超参**
- 结果（WSJ Section 23 F1）：

| 设置 | Transformer | 最强对手 |
| --- | --- | --- |
| 只用 WSJ | **91.3** | Dyer et al. RNNG **91.7** |
| 半监督 | **92.7** | Vinyals & Kaiser **92.1** |
| （多任务） | — | Luong et al. **93.0** |
| （生成式） | — | Dyer et al. RNNG **93.3** |

- 论文强调：在只有 **40K** 句的小数据条件下，Transformer 也超过了 BerkeleyParser（**90.4**），而之前的 RNN seq2seq（**88.3**）做不到

🔑 这个实验的作用是**说明它能用于翻译以外的任务**，不是要争 SOTA。但「迁移得很好」这个说法，靠的是**一个任务、几乎没调参**的结果。

---

## 7. 埋起来的洞察与论文内部的不一致

### 7.1 ⚠️ 不一致

1. **⚠️ 英法 BLEU：41.8 还是 41.0？**
   摘要和 Table 2 写 **41.8**；§6.1 正文写 *"our big model achieves a BLEU score of **41.0**"*。🔑 我的推测（**未核对 v1 原文**）：早期版本报的是 41.0，后来更新了摘要和表格，正文漏改了。**引用时以 Table 2 为准，并注明 v7。**
2. **⚠️ 引言「12 小时达到 SOTA」只对英德成立。**
   引言：*"can reach a new state of the art in translation quality after being trained for as little as twelve hours on eight P100 GPUs"*。12 小时的是 base，base 在英法上只有 **38.1**，不是 SOTA。
3. **⚠️ 句法分析：「只输给 RNNG」不完全对。**
   §6.3：*"yielding better results than all previously reported models with the exception of the Recurrent Neural Network Grammar [8]"*。但 Table 4 里 Luong et al. 的多任务模型 **93.0** 也比 Transformer 半监督的 **92.7** 高。可以说训练条件不同（多任务），但原文这句话没加限定。
4. **⚠️ BPE 引错了文献。**
   §5.1 *"Sentences were encoded using byte-pair encoding [3]"*，[3] 是 Britz et al.（*Massive exploration of NMT architectures*）。BPE 应该引 [31] Sennrich et al.，后者在 §4 被正确引用过。
5. **⚠️ 容易误读的 dropout。**
   §6.1 说英法 big 用 *"P_drop = 0.1, instead of 0.3"*。0.3 是 Table 3 里英德 big 的值，base 一直是 0.1。这不是矛盾，但三种设置散在三处，很容易记混：**base 0.1 / big 英德 0.3 / big 英法 0.1**。

### 7.2 ⭐ 从附录图里挖出来的

1. **⭐ Figure 3**（encoder layer **5/6**，`making` 一词）：大多数头指向远处的 `more difficult`，补全了 *making…more difficult* 这个短语。但仔细看，**有一个头的一部分权重落在 `<EOS>` 上**，还有几个头落在 `making` 自己和 `2009`、`laws` 上。🔑 「把注意力放到一个没有语义的 token 上」，后来被命名为 **attention sink**（StreamingLLM, Xiao et al. 2023，**课外补充**）。这张图里已经能看到这个现象的影子（**我从低分辨率图上读出来的，不确定程度中等**）。
2. **⭐ Figure 4**（layer 5，heads **5 和 6**）：`its` 的注意力**非常尖锐地**落在 `Law` 和 `application` 上，作者解释为**指代消解**。注意两个头给出了两个不同的先行词，所以更准确的说法是「两个头分别关注两个候选」，而不是「解决了指代」。
3. **⭐ 三张图都是 layer 5，都是 encoder self-attention，都是挑出来的例子。** 没有统计意义上的分析，所以 §4 *"many appear to exhibit behavior related to the syntactic and semantic structure"* 只是定性的观察。
4. **⭐ 作者贡献脚注**（第 1 页）：**Jakob** 提出用 self-attention 替换 RNN；**Noam** 提出了 scaled dot-product、multi-head 和不带参数的位置编码；**Ashish 和 Illia** 实现了第一个 Transformer。作者顺序是**随机**的。🔑 三个核心组件都出自同一个人。

---

## 8. 局限

论文**没有**单独的局限性章节。下面从正文里散落的自我承认中整理出来。

### 8.1 论文自己承认的

| 原文位置 | 原文 | 具体表现 | 🔑 更一般的问题 |
| --- | --- | --- | --- |
| §2 | *"reduced effective resolution due to averaging attention-weighted positions"* | 单头 softmax 只能输出一个加权平均 | **表达瓶颈**：softmax 只能做凸组合 |
| §4 | 长序列需要 restricted attention，*"plan to investigate"* | O(n²) 的计算和显存 | **二次方复杂度**，长上下文工程的根源 |
| §6.2 (B) | *"determining compatibility is not easy"* | d_k 变小就掉分 | 点积作为相似度**表达能力有限** |
| §6.2 (A) | *"quality also drops off with too many heads"* | 32 头比 8 头差 0.4 | 每个头维度太小时，头会**退化** |
| §5.4 | label smoothing *"hurts perplexity"* | PPL 变差、BLEU 变好 | **训练目标和评测指标不一致** |
| §7 | *"Making generation less sequential is another research goals"* | 解码仍然要逐 token 进行 | **训练可以并行，推理仍然串行** |

🔥 最后一条最重要：Transformer 解决的是**训练**的串行问题，**推理**的串行问题完全没动。今天推理系统要处理的东西（KV cache、continuous batching、speculative decoding），**都是从这一条衍生出来的**。论文在 §7 用一句话带过。

---

## 9. 在谱系里的位置

这篇和你读过的 agent 论文**不在同一层**。它是**基础层**：其它所有论文里的 LLM，内部都是它。

| | **Transformer** | BERT（Week 02 必读） | ReAct | Generative Agents | Voyager | SRA | RLVE |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 管哪一层 | **模型架构** | 预训练目标 | 推理-行动循环 | 长期记忆 | 程序性记忆（技能库） | 技能检索 | 训练数据 / 环境 |
| 核心机制 | self-attention + FFN | 双向 encoder + MLM | Thought/Action 交错 | 记忆流 + 反思 | 代码技能 + 自动课程 | 检索 skill | 可验证环境 + 自适应难度 |
| 「记忆」在哪 | **上下文窗口**（KV） | 上下文窗口 | 上下文（轨迹） | 外部记忆流 | 外部技能库 | 外部 skill 语料 | 权重 |
| 有没有 ground truth | **有**（人工参考译文） | 有（下游标签） | 有（EM / 成功率） | **没有** | 有（游戏状态） | 有 | **有**（程序判分） |
| 有没有 verifier | 没有（BLEU 是 n-gram 代理指标） | 没有 | 环境反馈 | **没有** | 有（GPT-4 critic） | — | **有**（程序） |
| 能主张什么 | **在 BLEU 上**更好、训练更便宜 | 下游任务更好 | 更准确、更可解释 | 只能主张**可信** | 能主张**完成了任务** | 检索 ≠ 会用 | 能主张**正确** |

🔑 一个贯穿全表的观察：Transformer 的「记忆」就是上下文窗口，读写都靠 attention。Generative Agents、Voyager、SRA 做的外部记忆和检索，本质上都是在**绕开 O(n²) 和上下文长度的限制**（§3.2）：把放不进窗口的东西存到外面，用的时候再取回来。**RAG 也是同一个思路。**

> **它不是这些 agent 论文的替代，而是它们下面的那一层。** Agent 论文研究的是怎么用一个固定的上下文窗口去组织外部世界；这篇论文决定了那个窗口长什么样、为什么贵。

### 9.1 ↔ 和课程的对照

- ↔ **Week 02（Embedding 与 Transformer 内部机制）**：讲义把 attention 讲成「可微分的近似字典查询」，并且和**现代 Hopfield network** 联系起来。本文 §3.2 的说法是 *"mapping a query and a set of key-value pairs to an output"*，两边的说法一致。注意 Week 02 讲义里的提醒：attention 是**模型内部的软检索**，**不等于** RAG 对外部知识库的检索。
- ↔ **Week 02 pooling**：这篇的 encoder 给**每个 token** 输出一个向量（§3 *"z = (z1, …, zn)"*），检索要的是**每个 chunk 一个向量**。中间的 pooling 这一步，原论文里没有，是 BERT / Sentence-BERT 才加上的。
- ↔ **Week 04 chunking pipeline**：这份 PDF 本身就是 chunking 实验的语料。🔑 这篇论文对 chunking 很不友好：Table 3 是一张多层表头的稀疏表格，公式 (1)–(3) 被 `pdftotext` 抽出来后上下标全乱了（比如 √d_k 变成了换行的 `√ dk`），附录的 attention 图抽出来只剩竖排的单词。**用它当语料时，表格和公式那几个 chunk 的检索质量值得单独检查。**
- ↔ **Week 05 memgraphrag**：同一份 PDF 又被用作知识图谱构建的语料。
- ↔ **2026-06-06 下午课记录（decoder-only block）**：课上讲的是**现代 decoder-only** block，和 2017 年原版有这些区别：

| | 2017 原版 | 现代 decoder-only（课外补充） |
| --- | --- | --- |
| 结构 | encoder-decoder | 只有 decoder |
| 归一化 | **Post-LN**，LayerNorm | Pre-LN，RMSNorm |
| 位置编码 | **正弦，加在输入上** | RoPE，作用在 Q、K 上 |
| FFN | **ReLU**，d_ff = 4d | SwiGLU / MoE |
| 注意力头 | **MHA**，每头独立的 K、V | MQA / GQA / MLA，多个头共享 K、V |

- ↔ **Awesome-ML-SYS-Tutorial 的 SGLang KV cache 笔记**：那篇里 `token_to_kv_pool` 对 MHA 的链接就指向本文。论文里的 decoder masked self-attention 在推理时每一步都要用到之前所有位置的 K、V，**KV cache 就是为这个存在的**，但论文完全没提推理时怎么实现。MQA / GQA / MLA 都是在缩小这个 cache。

---

## 10. 批判性分析

### 10.1 论文自己承认的

见 §8.1，不重复。

### 10.2 我自己补的

1. **复杂度论证有前提，而这个前提已经不成立了。** §4 的「self-attention 比 RNN 快」**明确依赖 n < d**（d = 512）。论文的场景是句子级翻译，这个前提成立；在今天的长上下文场景下，主要成本正好是 n² 那一项。论文给出的「O(1) 路径长度」好处仍然成立，但「计算更便宜」的好处是**有条件的**，引用时要把条件一起带上。

2. **消融没有方差，很多结论建立在噪声上。** Table 3 每行只跑了一次。⭐ §5.2 里 PPL 和 BLEU 排序经常不一致，说明 **±0.3 BLEU** 以内的差距不可靠。「16 头和 8 头一样好」「8 层不如 6 层」这类结论都撑不住。**值得做的复现**：在 base 配置上用 **5 个 seed** 重跑 Table 3 (A) 和 (C)，看头数和层数的排序还在不在。

3. **核心设计决策的理由是猜测，而且没有消融。**
   - √d_k 缩放：*"We suspect"*，没有「不缩放」的对照实验
   - 正弦编码能外推：*"may allow"*，没有外推实验，后来的研究还给出了相反的证据
   - 乘 √d_model：完全没有解释

   这些后来全都被改掉或者被重新解释过（RoPE、muP 一类的初始化/缩放研究）。🔑 论文的贡献在于**整体配方能训得动**，而不在于每个组件的理由都对。

4. **训练成本对比的口径不完全一致。** FLOPs 是用「时间 × GPU 数 × 估计峰值」算出来的，不是实测。论文没有说明前作的 FLOPs 是不是用同样方法估算的。英法的成本和英德共用一个数，而英法数据多 **8 倍**（⭐ §4.2）。「不到 1/4 成本」这个结论方向大概率是对的，但具体倍数不精确。

5. **big 的增益和 checkpoint averaging 混在一起了。**（⭐ §4.3）big 平均 **20** 个 checkpoint，base 平均 **5** 个。没有「big + 5 个 checkpoint」的对照，就没法知道 28.4 里有多少来自模型本身。

6. **只解决了训练的并行，没解决推理的串行，而且论文没量化推理成本。** 全文只报训练时间，没报解码速度、显存或者 KV cache 大小。推理时 decoder 每步都要对之前所有位置做 attention，**这正是今天推理系统的主要成本**，论文在 §7 只用一句话提到。🔑 这是这篇论文对 ML-SYS 方向最重要的一个空白。

---

## 11. 复习自测题

1. Scaled dot-product attention 除以的是什么？base 模型里这个数是多少？脚注 4 用什么统计假设解释为什么要除？
2. Base 模型的 N、d_model、d_ff、h、d_k 分别是多少？参数量多少？big 呢？
3. 为什么 8 个头、每头 64 维的总计算量和单头 512 维「差不多」？Table 3 (A) 里单头比最好配置差多少 BLEU？
4. Decoder 里有哪三个子层？encoder-decoder attention 的 Q 和 K、V 分别来自哪里？
5. 原文的 LayerNorm 放在残差的哪一边？现代 LLM 改成了什么？
6. 学习率公式是什么？warmup 多少步？base 的峰值学习率大约是多少？
7. Adam 的 β2 和 ε 是多少？和 PyTorch 默认值有什么不同？
8. Label smoothing 的值是多少？它对 PPL 和 BLEU 分别有什么影响？Table 3 (D) 里去掉它之后 PPL 是多少？
9. 正弦位置编码的波长范围是多少？作者选它而不选学习式编码的理由是什么？这个理由在文中被实验验证了吗？
10. 根据 Table 1，self-attention 在什么条件下比 RNN 的每层计算更便宜？base 模型的临界序列长度是多少？
11. 英德 big 的 BLEU 是多少，比之前最好结果高多少？英法 BLEU 在摘要和 §6.1 正文里分别写的是多少？
12. Base 和 big 分别平均了几个 checkpoint？这对理解 big 相对 base 的提升有什么影响？
13. Table 3 (C) 里，d_ff = 4096 和 d_model = 1024 哪个 BLEU 更高？各用了多少参数？
14. 句法分析实验用了几层？WSJ-only 和半监督的 F1 各是多少？Table 4 里有哪些模型比它高？

---

## 12. 核心数字速查表

| 项 | 值 |
| --- | --- |
| arXiv 版本 | 1706.03762**v7**（2023-08-02） |
| 会议 | NIPS 2017 |
| 作者数 / 顺序 | **8** 人，**随机** |
| N（encoder / decoder 层数） | **6 / 6** |
| d_model | **512**（big **1024**） |
| d_ff | **2048**（big **4096**），**4 倍** |
| h | **8**（big **16**） |
| d_k = d_v | **64** |
| 缩放因子 | 1/√d_k = **1/8** |
| embedding 乘以 | √d_model ≈ **22.6** |
| 每层参数（我算的） | attention ≈ **1.05M**，FFN ≈ **2.10M**（约 **2/3**） |
| 参数量 | base **65M**，big **213M** |
| PE 波长 | **2π** 到 **10000·2π** |
| 英德数据 | **4.5M** 句对，BPE **37000**（共享） |
| 英法数据 | **36M** 句，word-piece **32000** |
| Batch | 约 **25000** 源 + **25000** 目标 token |
| 硬件 | **8 × P100**（**9.5** TFLOPS） |
| base 训练 | **0.4 s/步**，**100K** 步，**12 h**（实算 **11.1 h**） |
| big 训练 | **1.0 s/步**，**300K** 步，**3.5 天** |
| Adam | β1 **0.9**，β2 **0.98**，ε **10⁻⁹** |
| Warmup | **4000** 步 |
| 峰值学习率（我算的） | base ≈ **7.0e-4**，big ≈ **4.9e-4** |
| Dropout | base **0.1** / big 英德 **0.3** / big 英法 **0.1** |
| Label smoothing | **0.1** |
| Checkpoint averaging | base **5** 个（每 **10 min**），big **20** 个 |
| Beam / α | **4** / **0.6** |
| 最大输出长度 | 输入 **+50**（句法分析 **+300**） |
| 英德 BLEU | base **27.3**，big **28.4**（之前最好 **26.36**，+**2.04**） |
| 英法 BLEU | base **38.1**，big **41.8**（§6.1 正文写 **41.0** ⚠️） |
| 训练 FLOPs | base **3.3e18**，big **2.3e19** |
| 英法领先 ConvS2S Ensemble（**41.29**） | +**0.51** |
| 英法 / 英德数据量 | **8 倍** |
| 英法成本比 | 不到 **1/4**（我算的 ≈ **0.19**） |
| 其它 GPU 算力 | K80 **2.8**，K40 **3.7**，M40 **6.0** TFLOPS |
| Table 3 base（dev） | PPL **4.92**，BLEU **25.8** |
| Table 3 big（dev） | PPL **4.33**，BLEU **26.4** |
| big − base 提升 | dev +**0.6** / test +**1.1** |
| 16 头 PPL / N = 8 PPL | **4.91** / **4.88** |
| d_k = 16 / 32 参数 | **58M** / **60M** |
| dropout / label smoothing 关闭值 | **0.0** |
| 单次运行噪声（我估的） | **±0.3 BLEU** |
| 单头 | **24.9**（−**0.9**） |
| 16 头 / 32 头 | **25.8** / **25.4** |
| d_k = 16 / 32 | **25.1** / **25.4** |
| N = 2 / 8 | **23.7** / **25.5** |
| d_model = 1024 | **26.0**，**168M** |
| d_ff = 4096 | **26.2**，**90M** |
| 不用 dropout | **24.6**（−**1.2**） |
| 不用 label smoothing | PPL **4.67**，BLEU **25.3** |
| 学习式位置编码 | **25.7** |
| 句法分析 | **4** 层，d_model **1024**，WSJ **40K**（词表 **16K**），半监督 **17M**（词表 **32K**） |
| 句法分析 F1 | WSJ-only **91.3**，半监督 **92.7** |
| 句法分析解码 | beam **21**，α **0.3** |
| 对手 F1 | RNNG **91.7** / **93.3**，Luong 多任务 **93.0**，BerkeleyParser **90.4**，RNN seq2seq **88.3** |
| 半监督对手 Vinyals & Kaiser | **92.1** |
| 今天长上下文的 n/d（我算的） | **16–32** 倍 |
| 附录图 | 全部是 encoder self-attention **layer 5 / 6**；Figure 4 是 heads **5、6** |
