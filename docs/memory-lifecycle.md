# 记忆生命周期与代码证据

Memory 分别管理证据、信念、召回轨迹、使用结果和策略。下面以一条偏好为例，说明当前实现和对应证据。

## 1. 从证据生成不可变修订

写入“晚上喝低因咖啡”后，系统保存 Observation 和 EvidenceSpan，再创建记忆及其修订。
如果用户改为“晚上喝花草茶”，系统追加新 Revision，旧版本保留；Scope 与幂等键限定操作范围。
同键异参会被拒绝，修正还可携带预期版本，避免覆盖并发产生的新状态。

- 实现：[领域对象](../src/evolvable_memory/domain/memory.py)、[应用服务](../src/evolvable_memory/application/service.py)。
- 测试：[test_memory_application.py](../tests/test_memory_application.py) 中的
  `test_correction_preserves_history_and_recall_uses_new_head`、
  `test_correction_rejects_a_stale_expected_revision_but_allows_its_retry`。

## 2. 用两个时间边界选择可见状态

`valid_at` 指定业务时点，`known_at` 限制系统截至何时已经记录的信息。
系统从不可变修订链选择可见版本，同时限定 Outcome 的知识时间。
评分使用请求执行时的 StrategySnapshot，因此这里重建的是历史可见状态。

- 实现：[应用服务](../src/evolvable_memory/application/service.py)、[历史状态架构](architecture.md)。
- 测试：[test_memory_application.py](../tests/test_memory_application.py) 中的
  `test_as_of_recall_is_scope_local_read_only_and_reproducible`、
  `test_as_of_recall_uses_only_outcomes_known_at_the_query_time`。

## 3. 召回并冻结 Trace

内存快速开始使用词法召回；默认 Compose 使用词法与 Milvus 候选。
向量候选仍需由权威存储复核 Scope 和双时间可见性。默认 embedding 是 384 维确定性哈希基线，
semantic 分量取词法与向量分量的最大值，最终评分还考虑上下文、信念、效用与时效。

服务构造 RecallTrace 并调用 `save_trace()`：命中修订、评分、策略与时间边界随之固定。
**召回不强化 Belief 或 Utility，但会追加 Trace。**

Trace 上下文投影按字符预算做确定性排序抽取和精确去重，保留逐片段 Revision 归因及摘要校验。

- 实现：[召回服务](../src/evolvable_memory/application/service.py)、
  [embedding](../src/evolvable_memory/adapters/embeddings.py)、
  [上下文投影](../src/evolvable_memory/application/compression.py)。
- 测试：[test_memory_application.py](../tests/test_memory_application.py) 中的
  `test_recall_does_not_reinforce_belief_or_utility`；
  [test_projection.py](../tests/test_projection.py) 中的
  `test_hybrid_recall_revalidates_vector_candidates_against_authority`；
  [test_compression.py](../tests/test_compression.py) 中的
  `test_projection_is_attributable_deterministic_and_read_only`。

## 4. 将 Outcome 归因到实际召回

应用提交反馈时，服务检查 Trace、Revision、Scope 和幂等关系，再更新相应上下文的 Utility。
重复反馈和错误归因分别有明确的处理规则。提供 MemoryUsage 凭证的消费路径还会验证投影交付关系。

- 实现：[经验对象](../src/evolvable_memory/domain/experience.py)、[应用服务](../src/evolvable_memory/application/service.py)。
- 测试：[test_memory_application.py](../tests/test_memory_application.py) 中的
  `test_attributable_outcome_updates_contextual_utility_once`、
  `test_outcome_requires_trace_membership_and_scope`、
  `test_usage_receipt_binds_outcome_to_the_delivered_projection`。

## 5. 受控更新策略

候选策略是不可变快照。实验记录提案、离线、影子、灰度、晋升和回滚阶段，
可信内部编排验证 Gate Receipt；晋升或回滚与活动策略切换原子提交。
阶段记录是内部状态机，真实 shadow/canary 流量编排、外部产物摘要复核和授权控制面仍需补充。
身份、授权、Scope、删除和审计规则保持固定。

- 实现：[策略领域](../src/evolvable_memory/domain/evolution.py)、
  [演化编排](../src/evolvable_memory/application/evolution.py)、[演化安全](evolution-safety.md)。
- 测试：[test_evolution_application.py](../tests/test_evolution_application.py) 中的
  `test_gated_experiment_promotes_and_rolls_back_atomically`、
  `test_experiment_cannot_skip_gates_or_move_time_backwards`。

## 持久化和验证范围

PostgreSQL 是持久化模式下的权威存储。写入事务追加 outbox，独立 worker 以租约消费事件，
更新 Milvus；重试、死信、游标、重建与删除屏障见[Milvus 投影指南](milvus-projection.md)。

上述名称是源码中的代表性测试入口。内存测试、模拟 Milvus 测试与真实数据库／浏览器测试的证据范围不同，
是否通过应以对应提交的运行记录为准。两套内置 synthetic 评测用于契约回归；
数据集和指标说明见[评测指南](evaluation.md)，部署范围见[当前实现与运行边界](runtime-scope.md)。
