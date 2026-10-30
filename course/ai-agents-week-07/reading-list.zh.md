# Week07 阅读与来源核实清单

来源：[lesson plan](uploads/fall-agents-week-7-lesson-plan.pdf) 印刷 pp.26–30。这里按讲义列出书目，**不表示已经读过论文、已验证论文版本或所有实验数字**。链接和编号来自讲义，本次没有联网核实。

## 四篇必读（讲义明确要求）

| 顺序 | 文献 | 读的时候回答什么 |
| --- | --- | --- |
| 1 | [GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning](https://arxiv.org/abs/2507.19457) | 重点 §2–3；frontier 的坐标、两个池、预算；与 GRPO 比较的限定条件 |
| 2 | [DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines](https://arxiv.org/abs/2310.03714) | signature/module/compile 如何把程序与 prompt 分离 |
| 3 | [Agentic Context Engineering](https://arxiv.org/abs/2510.04618) | 为什么积累增量而不是整体重写；context collapse 如何测量 |
| 4 | [SkillOpt: Executive Strategy for Self-Evolving Agent Skills](https://arxiv.org/abs/2605.23904) | 有界编辑、拒绝历史、epoch 更新、gate 各解决什么 |

## 选读路线（本笔记安排）

- 文本反馈来历：[OPRO](https://arxiv.org/abs/2309.03409) → [ProTeGi](https://arxiv.org/abs/2305.03495) → [TextGrad](https://arxiv.org/abs/2406.07496)。
- 多模块优化对照：[MIPROv2](https://arxiv.org/abs/2406.11695)。
- 审视 judge：[From Raw Experience to Skill Consumption](https://arxiv.org/abs/2605.23899)。
- 严格 gate 的反方：[SkillNEO](https://arxiv.org/abs/2610.20926)，对照 SkillOpt 的相同任务/预算再判断。
- 简单搜索基线：[Naive Prompt Optimization](https://arxiv.org/abs/2608.27266)。
- 工程 skill 案例：[gskill 博客](https://gepa-ai.github.io/gepa/blog/2026/02/18/automatically-learning-skills-for-coding-agents/)。

## 配套材料（尚未取得）

- Reservoir：讲义指定 §5 GEPA，§12 run playbook；§6 judge；§7 成本；§9 skills；§10 多轮 credit assignment；§11 pattern language。
- Workshop / Exam 两个 kit 与两张卡片。
- Week06 No Castle Without Walls。

## 需要独立核实的主张

| 讲义主张 | 核实点 |
| --- | --- |
| GEPA 与 GRPO / MIPROv2 的收益与 rollout 倍数 | 论文版本、任务、模型、预算、百分点或相对比例 |
| 库支持四类 frontier、不同默认值 | 实际安装版本、入口参数、源码行为 |
| DSPy 3.4 / ReAnchor / Flex 等接口 | 官方 release 与当前 API；不要只复制讲义代码 |
| 无 rubric 46.4%，有 rubric 73.8% | 样本、评分参照、置信区间、是否同一设置 |
| 49% 优化运行退步 | 保留单一模型、四任务、72 次运行等边界 |
| SkillOpt 与 SkillNEO 的 gate 取舍 | 是否同预算、如何选择最终结果、holdout 是否被反复使用 |

课前目标是带着问题进课堂，不把全部选读当作周日前的额外必修。
