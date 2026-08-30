# Approval Policy

> 状态：`WORKING`

## 原则

- AI 可以创建 `WORKING` 内容。
- 核心规则、模板、架构决定和长期记忆必须由 Founder 明确批准。
- 批准必须留下 Decision Record；仅移动文件或修改状态字段不构成批准。
- Canonical Authority 必须来源明确、版本可追溯、通过适用验证，并绑定固定 Commit 与 Release Evidence。
- 自动化不得代替 Founder 作出批准。

## 资产类别与成熟度分离

- `SOURCE` 是原始证据类别，不是 Promotion 状态；原件保持只读，可登记校验和、来源和获取时间。
- `GENERATED` 是派生产物类别，不因生成成功而获得 Canonical Authority。
- 规则、模板、配置、Registry 等受治理资产使用最小状态流：

`WORKING → APPROVED → ARCHIVED`

评审中的内容通过路径、Pull Request 或 Review 记录表达，不增加 `CANDIDATE` 状态；被替代内容进入 `ARCHIVED` 并记录 replacement reference。

`TEMP`、`CACHE`、`LOG` 不进入 Promotion 流程。

## 批准证据

批准记录必须绑定：Artifact Stable ID、版本或 Git Commit、内容 SHA-256、批准人、批准时间、批准范围和附带条件。仅口头同意、移动目录或修改 `artifact_state` 不构成可验证批准。

涉及外部数据传输、外部发布、不可逆删除、Secret/Credential 或权限升级时，模板批准不能替代单次操作授权。
