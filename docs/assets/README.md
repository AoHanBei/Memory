# 文档素材

## 架构图

`evolvable-memory-technical-architecture.svg` 是可编辑源文件，同名 PNG 由 SVG 渲染。
更新时同时核对请求、Trace、Outcome、策略与存储的代码合同，并重新生成 PNG。

图中的反馈与策略更新是独立操作。策略实验阶段持久化已实现；真实 shadow/canary
流量编排仍待实现。上下文投影已经提供字符预算内的确定性抽取与精确去重。

## 工作台截图

`memory-recall.png` 和 `memory-revisions.png` 来自本仓库实际前端与临时内存 API。
脚本写入合成偏好、追加修正，通过界面召回、提交反馈并打开修订历史。
截图带有 **SYNTHETIC DEMO DATA** 标记。

这是本机内存模式的功能演示。PostgreSQL、Milvus、生产身份与性能有各自的验证流程。
服务只监听临时回环端口，生成过程不使用真实用户数据、外部模型或持久化数据库。

在仓库根目录复现：

```bash
uv sync --locked
uv run playwright install chromium
uv run python examples/capture_docs.py
```

也可以使用已安装的 Chromium 浏览器：

```powershell
uv run python examples/capture_docs.py --browser-executable 'C:\Program Files\Google\Chrome\Application\chrome.exe'
```

`screenshots.json` 记录代码基线、界面源文件、生成脚本与浏览器版本。
脚本同时从 SVG 重新渲染架构 PNG，并检查图中文字边界。
结束时关闭两项本地服务，内存演示数据随进程释放。
