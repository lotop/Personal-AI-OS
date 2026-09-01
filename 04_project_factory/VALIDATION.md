# Project Factory Validation

> 状态：`APPROVED`
>
> Canonical Authority：`FOUNDER_APPROVED (PAOS-018)`

新项目进入 `PROVISIONAL` 前必须验证：

- `project_id` 和 Slug 在 Registry 中唯一。
- 目标路径不存在、父目录预先存在，且不在 Personal AI OS 或其他 Git Repository 内。
- 根级入口文件存在并可读取。
- `project.toml` 可解析且 Schema 版本存在。
- Approved Template Pack 的 path + file SHA-256 Digest 与 Factory 外部登记值一致。
- 所有生成文件能追溯到 PAOS/Factory/Template 版本、Approval Reference、Pack Digest 与逐文件 SHA-256。
- Source、Working、Generated、Archive、Temp 边界明确。
- 没有真实 Secret、绝对用户路径或悬空引用。
- Git Repository 可初始化，默认分支符合策略。
- `.paos-init.json` 使用稳定 V0.2 Schema，项目状态为 `PROVISIONAL`，并单独记录 Template 状态。
- Registry Candidate 只包含候选数据，不产生 OS Registry 写入副作用。
- 首张正式 Task Card 未被虚假预填；只提供空白任务模板。
- 初始化报告包含创建清单、验证结果和回滚步骤。

当前 Approved `PROJECT_SCAFFOLD` Pack 为 `01_templates/project-base-pack`；Release M3 会对每个此类 Pack 执行真实 Dry Run。`ARTIFACT_LIBRARY` Pack 只提供可复用模板内容，不得由 Project Factory 当作项目脚手架实例化。

Factory 单元测试必须覆盖固定 Digest 向量、Digest 漂移拒绝、Working Apply 拒绝、V0.2 安装基线、统一 `PROVISIONAL` 状态、缺失父目录拒绝、最终替换前二次目标检查、Git 失败回滚和 Approved Pack E2E。
