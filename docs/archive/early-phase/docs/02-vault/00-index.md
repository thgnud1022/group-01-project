# Project Vault Index - ProcureAI

## Purpose

Đây là điểm vào của Project Vault ProcureAI. Requirement và Business Rule đã xác nhận là nguồn sự thật cho nghiệp vụ mua sắm.

## Source-of-truth map

| Area | Primary source | Context source |
|---|---|---|
| Requirements | [5.requirements.md](02-requirements/5.requirements.md) | [Discovery Requirements](../01-discovery/5.requirements.md) |
| Business Rules | [business_rules.md](03-domain/business_rules.md) | [Discovery Business Rules](../01-discovery/6.business-rules.md) |
| Workflow | [workflows.md](03-domain/workflows.md) | [Discovery Requirements](../01-discovery/5.requirements.md) |
| Project context | [Project Charter](../01-discovery/1.project-charter.md) | [User Research](../01-discovery/2.user-research.md) |
| Domain terms | [glossary.md](03-domain/glossary.md) | [Discovery Glossary](../01-discovery/4.glossary.md) |
| Research evidence | [user-research.md](01-sources/2.user-research.md) | [Discovery Research](../01-discovery/2.user-research.md) |
| Product interpretation | [Product documents](../03-product/) | Requirements and Business Rules |
| Governance | [source-priority.md](source-priority.md) | [AI Usage Log](AI_USAGE_LOG.md) |

## Artifact directory

- `01-sources/`: research and source documents
- `02-requirements/`: confirmed Requirements
- `03-domain/`: glossary, Business Rules and workflow
- `08-decisions/`: confirmed decisions when recorded
- `AI_USAGE_LOG.md`: AI usage and human verification

## Retrieval rules

1. Requirement and Business Rule đã xác nhận có priority cao nhất.
2. Project Charter cung cấp context về Problem, Users, MVP và Success Metrics.
3. User Research cung cấp evidence về nhu cầu và pain point.
4. Product, Design, Technical và Prototype chỉ diễn giải, không tự tạo rule mới.
5. Khi thiếu dữ liệu, ghi `KHÔNG ĐỦ DỮ LIỆU` và chỉ rõ nguồn cần bổ sung.
6. Khi có xung đột, không tự chọn nguồn thấp hơn; tạo Open Question hoặc Decision để con người xác nhận.

## Citation format

- Requirement: `REQ-FR-*`, `REQ-NFR-*` + `02-requirements/5.requirements.md`
- Business Rule: `REQ-BR-*` + `03-domain/business_rules.md`
- Constraint: `CON-*` + `03-domain/business_rules.md`
- Research evidence: `P1`–`P5` + `01-sources/2.user-research.md`
- Open question: `Q-*` + `01-discovery/5.requirements.md`
