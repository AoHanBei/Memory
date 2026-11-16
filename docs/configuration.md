# 配置参考

应用直接读取环境变量，不会自动加载 `.env` 文件。可参考 [.env.example](../.env.example)：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `EMF_ENVIRONMENT` | `development` | `development`、`test`、`staging` 或 `production` |
| `EMF_HOST` | `127.0.0.1` | 后端监听地址 |
| `EMF_PORT` | `38089` | 后端端口 |
| `EMF_LOG_LEVEL` | `INFO` | Uvicorn 日志级别 |
| `EMF_STORE` | `memory` | 存储实现：`memory` 或 `postgres` |
| `EMF_DATABASE_URL` | 空 | PostgreSQL DSN；`EMF_STORE=postgres` 时必填 |
| `EMF_DATABASE_POOL_MIN_SIZE` | `1` | PostgreSQL 最小连接池大小 |
| `EMF_DATABASE_POOL_MAX_SIZE` | `10` | PostgreSQL 最大连接池大小 |
| `EMF_DATABASE_READINESS_TIMEOUT_SECONDS` | `1.0` | `/readyz` 专用连接池等待上限，范围 0.05–30 秒 |
| `EMF_PROJECTION_MODE` | `disabled` | `disabled` 或 `milvus`；默认 Compose 设为 `milvus` |
| `EMF_PROJECTION_REQUIRED` | `false` | 为 `true` 时 Milvus 故障会使 `/readyz` 失败；默认允许词法降级 |
| `EMF_MILVUS_URI` | `http://127.0.0.1:19530` | Milvus SDK 地址 |
| `EMF_MILVUS_COLLECTION` | `evolvable_memory_v1` | 可重建的共享投影 collection |
| `EMF_EMBEDDING_PROVIDER` | `hash` | 离线 `hash` 或 `openai_compatible` |
| `EMF_EMBEDDING_DIMENSIONS` | `384` | collection 向量维度；变更后应使用新 collection 或重建 |
| `EMF_MAX_REQUEST_BODY_BYTES` | `1048576` | API 请求体最大字节数 |
| `EMF_AUTH_MODE` | `development` | `development` 本机身份或 `jwt` 可信 access token |
| `EMF_AUTH_JWT_ISSUER` | 空 | JWT issuer；`jwt` 模式必填 |
| `EMF_AUTH_JWT_AUDIENCE` | 空 | 当前 API 的 JWT audience；`jwt` 模式必填 |
| `EMF_AUTH_JWT_JWKS_URL` | 空 | IdP 公钥集合 URL；`jwt` 模式必填 |
| `EMF_AUTH_JWT_ALGORITHMS` | `RS256` | 允许的非对称签名算法，逗号分隔 |
| `EMF_AUTH_REQUIRED_SCOPE` | `memory` | token 必须包含的粗粒度 OAuth scope |
| `EMF_AUTH_AUDIT_HMAC_KEY` | 空 | 授权审计引用 HMAC 密钥；`jwt` 模式至少 32 字符 |
| `EMF_AUTH_AUDIT_SINK` | `log` | `log` 或生产用 `postgres` |
| `EMF_GOVERNANCE_MODE` | `development` | `development` 或强制门禁的 `postgres` |
| `EMF_GOVERNANCE_HMAC_KEY` | 空 | 持久治理 HMAC 密钥；至少 32 字符 |
| `EMF_GOVERNANCE_PSEUDONYM_KEY_ID` | `governance-v1` | HMAC 伪名密钥版本 |
| `EMF_PRIVACY_POLICY_VERSION` | `privacy-v1` | 治理对象绑定的策略版本 |
| `EMF_FRONTEND_URL` | `http://127.0.0.1:33009` | 服务发现返回的前端地址 |
| `EMF_PUBLIC_API_URL` | `http://127.0.0.1:38089` | 后端服务发现、前端请求和前端 CSP 共用的对外 API 基础地址 |
| `EMF_CORS_ORIGINS` | 两个本机前端 Origin | 逗号分隔的允许来源 |
| `EMF_FRONTEND_HOST` | `127.0.0.1` | 前端监听地址 |
| `EMF_FRONTEND_PORT` | `33009` | 前端端口 |

运行方式与生产试点配置见[部署指南](deployment.md)。
