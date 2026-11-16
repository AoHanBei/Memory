# 当前实现与运行边界

当前版本以可运行的偏好记忆闭环为核心，以下范围用于解释实现和验证结果：

- 原生快速开始的内存模式不持久化，后端重启即清空；PostgreSQL 是默认 Compose 的权威存储，但其故障恢复和生产运维仍处于开发预览。
- 默认 Compose 已实现词法 + Milvus 向量的混合召回；原生内存模式仍只使用词法召回。默认离线 hash embedding 是确定性基线，不等于生产语义模型质量。
- Trace 上下文压缩当前只提供确定性排序抽取与精确去重，预算按字符而不是模型 token 计算；尚未实现 LLM 摘要、模糊语义聚类或物理遗忘。
- 双时间召回会按 `valid_at` / `known_at` 重建 Revision 和 Outcome 可见性，但仍使用执行时的 `StrategySnapshot`；它不是完整历史策略 replay。
- `0003_bitemporal_recall` 会为旧 Outcome 近似回填系统记录时间。旧 Schema 没有保存真实摄入时点，因此迁移结果只能用于 best-effort 历史边界，不能当作精确历史审计事实。
- 内置 `smoke-v1` / `temporal-v1` 只证明当前提交通过对应 synthetic 契约，不能外推为 LongMemEval、LoCoMo、SOTA 或真实业务质量；时间线回放也不是完整历史策略 replay。
- 开发模式仍把 `tenant_id` 和 `subject_id` 作为本地目标 Scope；JWT 模式只接受 token 中同一条 `memory_access` grant 明确覆盖的目标。
- 已实现可信 JWT、类型化授权、purpose + ProcessingGrant 双门禁、Scope 抑制/删除、最小证明和 PostgreSQL append-only 授权审计；尚未实现成员/角色管理 API、token 撤销、临时授权、RLS、自动保留扫描和备份到期治理。
- Milvus 专用 outbox 消费、租约/重试/死信、投影游标、全量重建和删除屏障已经实现；通用事件发布、授权后的运维重放 API与积压告警仍未完成。
- 尚未定义并验证生产 SLO、告警、备份恢复和灾难恢复目标。
- 演化模块只能调整有界策略参数，不能修改授权、隔离、删除或审计规则。
- 当前具备可信内部 `EvolutionApplication` 的阶段持久化、HMAC-SHA256 Gate Receipt 验证与原子 promotion/rollback，但没有授权后的 HTTP/API 控制面；系统只验证签发方声明，尚未抓取外部评测产物复核内容摘要、独立持久化完整 Receipt 或自动执行真实 shadow/canary 流量，不能把阶段标签当作质量证明。

计划中的生产方向包括权限治理控制面、数据库 RLS、隐私生命周期、PostgreSQL 故障恢复与迁移加固、通用事件发布与受控重放、图检索、生产 SLO 和代表性离线回放评估，详见 [路线图](../ROADMAP.md)。Milvus 的运行与恢复见 [Milvus 投影指南](milvus-projection.md)。
