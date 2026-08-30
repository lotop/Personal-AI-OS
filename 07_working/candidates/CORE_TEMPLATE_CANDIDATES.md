# Core Template Candidates｜V1.1.2

> 状态：`WORKING`
>
> 日期：`2026-08-31`
>
> Canonical Authority：`NONE`

本索引登记 V1.1.2 核心模板候选。所有文件均可继续研究和测试，但必须逐个获得 Founder Approval 后才能迁入 `01_templates/` 或成为 Canonical Rule。

| 顺序 | Candidate | 层级 | 维护者 | Source of Truth | 主要关系 | 状态 |
|---|---|---|---|---|---|---|
| 1 | `DECISION_RECORD_TEMPLATE.md` | Global / Project | Decision Owner | 否，批准后才是模板源 | `DECISIONS.md`、Release Approval | 待确认 |
| 2 | `PROFILE_TEMPLATE.md` | Global | Founder | 否 | Identity、Preferences | 待确认 |
| 3 | `PREFERENCES_TEMPLATE.md` | Global | Founder | 否 | Profile、Mode | 待确认 |
| 4 | `COMMUNICATION_TEMPLATE.md` | Global | Founder | 否 | Preferences、Agent Adapter | 待确认 |
| 5 | `MODE_TEMPLATE.md` | Mode | Governance Owner | 否 | CHAT / WORK / REVIEW | 待确认 |
| 6 | `MEMORY_TEMPLATE.md` | Global / Project | Knowledge Owner | 否 | Source、Decision、Knowledge | 待确认 |
| 7 | `KNOWLEDGE_EXTRACTION_TEMPLATE.md` | Task / Session | Task Owner | 否 | Memory Pipeline、Session Close | 待确认 |
| 8 | `TASK_CARD_TEMPLATE.md` | Task | Task Owner | 否 | Concurrency、Validation | 待确认 |
| 9 | `SESSION_CLOSE_TEMPLATE.md` | Session | Session Owner | 否 | Memory、Decisions、Handoff | 待确认 |
| 10 | `HANDOFF_TEMPLATE.md` | Task | Current Owner | 否 | Task Card、Validation | 待确认 |
| 11 | `SKILL_REGISTRY_TEMPLATE.toml` | Global Registry | Skill Owner | 否 | `02_registry/skills.toml` | 待确认 |
| 12 | `GC_PLAN_TEMPLATE.json` | Lifecycle / Machine Evidence | Lifecycle Owner | 否 | GC Policy、Cleanup Harness | 待确认 |

当前第一个应逐项讨论确认的模板是 `DECISION_RECORD_TEMPLATE.md`。
