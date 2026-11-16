# 项目背景与开发方式

[Memory](https://github.com/AoHanBei/Memory) 是由
[AoHanBei](https://github.com/AoHanBei) 维护的个人 AI 应用记忆项目，重点实践证据归因、
不可变修订、双时间召回、结果效用学习和受控策略更新。

## 设计与实现

项目将 Evidence、Belief、Experience、Projection 和 Evolution 分开建模。
PostgreSQL 保存权威状态，Milvus 提供可重建的检索投影；领域层保持纯 Python，
API 与基础设施通过 application 端口连接。设计取舍和具体实现见
[架构说明](docs/architecture.md)与[领域边界决策](docs/adr/0001-layer-and-plane-boundaries.md)。

开发参考相关开源项目的思路，并使用 AI 辅助实现。代码大部分由 AI 辅助生成，
维护者负责问题定义、设计取舍、验收标准、测试与 diff 审查。
项目能力以当前源码为依据，验证结论对应具体测试、数据集和运行记录。

## 维护与许可

项目仓库、问题反馈和安全报告由 AoHanBei 维护。项目采用
AGPL-3.0-only，许可证全文见 [LICENSE](LICENSE)。

测试工具使用 Deque Systems 维护的 `axe-core`，通过 `package-lock.json` 锁定为
4.11.4，采用 MPL-2.0。它用于本地 Chromium 无障碍审计，安装在忽略的
`node_modules/` 中，不作为运行时前端依赖，也不复制进应用镜像或 Python 发行包。
