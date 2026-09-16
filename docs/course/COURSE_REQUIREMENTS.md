# COURSE REQUIREMENTS
# MIS3032 — Thực hành Lập trình Ứng dụng Doanh nghiệp bằng AI

## 1. PURPOSE

This document summarizes the course requirements that govern the
AI-assisted development project.

This document is derived from the lecturer's course materials.

IMPORTANT:
- The lecturer's original materials are the source of truth.
- This file is a working context file for AI-assisted development.
- If this file conflicts with the latest lecturer-approved requirement,
  the latest lecturer-approved requirement takes priority.
- AI must not invent or change business requirements.

---

# 2. CORE PRINCIPLE

AI provides development speed.

Students remain responsible for:

- requirements
- business decisions
- scope
- verification
- code quality
- testing
- security
- final acceptance

AI output must never be accepted blindly.

Important outputs must have verifiable artifacts and evidence.

---

# 3. MANDATORY AI WORKFLOW

Every important AI-assisted task follows:

Context
→ Plan
→ Generate
→ Verify
→ Integrate
→ Learn/Reuse

## Context

Provide AI with:

- correct source
- requirement IDs
- current version
- relevant files
- glossary
- constraints
- task scope

## Plan

AI must explain its proposed approach before producing
large outputs or making significant code changes.

Human reviews the plan.

## Generate

AI produces:

- documents
- designs
- code
- tests
- analysis

according to the approved scope and output format.

## Verify

Human must verify AI output using appropriate evidence:

- source comparison
- requirement comparison
- diff review
- tests
- lint
- build
- manual verification
- browser verification
- security review

## Integrate

Only verified output may be integrated into:

- requirements
- documentation
- backlog
- codebase
- tests
- release

## Learn / Reuse

Record:

- useful prompts
- reusable workflows
- recurring AI mistakes
- lessons learned
- reusable rules

---

# 4. AI USAGE RULES

## AI MUST NOT independently decide:

- business requirements
- scope changes
- prices
- inventory
- totals
- permissions
- order status
- critical business data
- information not provided by requirements or approved sources

If information is missing:

- mark UNKNOWN
- mark TBD
- ask a clarification question

Do not silently invent information.

AI must not claim:

- "test passed"
- "deployment succeeded"
- "bug fixed"

unless there is recent execution evidence.

AI review saying "looks good" is NOT sufficient
for merging code.

Human must inspect the diff and run appropriate checks.

---

# 5. PROMPT STANDARD

For important tasks, prompts should contain:

1. ROLE
2. GOAL
3. CONTEXT
4. INPUT
5. RULES
6. OUTPUT
7. VERIFY

Example:

ROLE:
You are acting as a QA Engineer.

GOAL:
Verify US-09 / T-094.

CONTEXT:
Provide requirement IDs, source files, business rules
and relevant implementation.

INPUT:
Only use approved project documents and source code.

RULES:
Do not invent business rules.
Mark missing information as UNKNOWN.

OUTPUT:
Return test scenarios and expected results.

VERIFY:
Check missing cases, edge cases, security and regression risks.

---

# 6. REQUIRED PROJECT ARTIFACTS

The project should maintain traceable artifacts including,
as applicable:

- Project Index
- Project Charter
- Research notes
- Research synthesis
- Requirements
- Glossary
- Business Rules
- MVP scope
- Out of Scope
- Project Vault
- Source Priority
- Q&A Benchmark
- AI Usage Log
- PRD
- User Stories
- Acceptance Criteria
- Taiga Epic / Story / Task
- Figma design
- Design System
- User Flow
- Architecture
- ERD / Data Model
- API Contract
- Story Specifications
- Test Plan
- Test Cases
- Test Reports
- Pull Requests
- Decision Log / ADR
- README / Runbook
- Deployment information
- Traceability Matrix
- Demo evidence

---

# 7. PROJECT VAULT / SOURCE PRIORITY

When sources conflict, do not silently choose a lower-priority source.

Recommended source priority:

1. Latest lecturer-approved business rules / requirements
2. Approved ADR / Decision Log
3. Current PRD
4. Current User Story / Acceptance Criteria
5. Prototype / Figma
6. AI chat output that has not yet been integrated

If two sources conflict:

- identify the conflict
- do not guess
- create an open question or decision
- obtain human confirmation

---

# 8. REQUIREMENT QUALITY

Requirements should be:

- clear
- testable
- traceable
- uniquely identifiable

Use stable IDs such as:

REQ-01
REQ-02

NFR-01
NFR-02

BR-01
BR-02

CON-01

ASM-01

Q-01

Do not change an ID when only wording changes.

Each requirement should record:

- source
- priority
- confidence where applicable
- status

---

# 9. USER STORIES

The project should contain approximately 8–15 User Stories.

Each User Story should contain:

- Story ID
- Epic
- Title
- User / Actor
- Goal
- Benefit
- Acceptance Criteria
- Priority
- Dependencies
- Requirement traceability

Each User Story should normally have
2–6 Acceptance Criteria.

Must-have stories must have traceability.

---

# 10. TASKS

Each implementation task must have:

- Task ID
- Related User Story
- Owner
- Expected output
- Scope
- Verification criteria

Tasks should be small enough to implement and verify independently.

Do not combine unrelated features into one large AI coding request.

---

# 11. TRACEABILITY

Every important Must requirement should be traceable through:

Requirement
→ User Story
→ Task
→ Design
→ Code / Pull Request
→ Test
→ Evidence
→ Release

No Must requirement should become orphaned.

---

# 12. TESTING / QUALITY

Testing should cover, where applicable:

- happy path
- failure path
- validation
- permission
- business rules
- edge cases
- boundary cases
- regression

Important business rules require explicit tests.

Do not report PASS unless the test has actually been executed.

---

# 13. DEFINITION OF DONE

A Must-have story is considered complete only when
the applicable conditions are satisfied.

At minimum:

- Acceptance Criteria pass
- implementation exists
- tests exist and pass
- relevant verification has been performed
- no unresolved critical issue remains
- traceability is updated
- required evidence exists

For the overall project, the course requires attention to:

- Must-have stories passing AC
- latest build and automated tests passing
- no secrets committed
- accessible deployment URL
- README / runbook sufficient for another team member
  to set up the project
- no orphaned Must requirements in the Traceability Matrix

---

# 14. AI USAGE LOG

Every significant AI-assisted activity should record:

- Task
- Input / Context
- AI / Tool
- Prompt / Skill
- Output
- Human Verification
- Decision
- Time where required

Example:

Task:
T-094 — Ensure PO price and quantity match quotation

Input / Context:
US-09, T-094, business rules, API contract, relevant source files

AI / Tool:
Kiro

Prompt / Skill:
Story implementation / QA review

Output:
Implementation plan, code changes, tests

Human Verification:
Reviewed diff and executed tests.

Decision:
Accepted only after verification.

---

# 15. EVIDENCE

Evidence should demonstrate the actual development process.

Useful evidence includes:

- AI conversation
- prompt
- AI plan
- generated artifact
- code diff
- commit
- Pull Request
- test execution
- test report
- browser result
- Figma version
- Taiga task
- deployment result
- human decision

Screenshot is supporting evidence.

The original artifact remains the primary evidence.

---

# 16. HUMAN-IN-THE-LOOP

The human must remain responsible for:

- requirement acceptance
- business decisions
- scope decisions
- architecture decisions
- reviewing AI output
- reviewing code diff
- test verification
- release decisions

AI is an assistant, not the project owner.

---

# 17. DEVELOPMENT WORKFLOW

For each important User Story:

1. Understand the requirement.
2. Identify dependencies.
3. Confirm Acceptance Criteria.
4. Review existing source code.
5. Create implementation plan.
6. Human approves plan.
7. Implement a small task.
8. Review code diff.
9. Run tests.
10. Fix problems.
11. Run regression tests.
12. Update documentation.
13. Update traceability.
14. Record AI Usage Log.
15. Commit / Pull Request.
16. Prepare evidence.

---

# 18. DO NOT DO

Do NOT:

- give AI one giant prompt and blindly copy the result
- let AI invent requirements
- let AI silently change scope
- trust undocumented assumptions
- claim tests passed without execution
- merge only because AI says "looks good"
- skip code diff review
- skip human verification
- create documentation that does not match the source code
- create fake evidence after the work is finished

---

# 19. CURRENT PROJECT

Project:

AI Procurement & Purchase Approval System

Current backlog structure:

EPIC
→ User Story
→ Task

The implementation must preserve traceability from
course requirements to project artifacts and source code.

---

# 20. AI AGENT RULE

When working on this project, AI should:

1. Read the relevant context first.
2. Identify the exact scope.
3. State assumptions explicitly.
4. Identify missing information.
5. Create a plan.
6. Wait for human approval when the task is significant.
7. Make controlled changes.
8. Explain what changed.
9. Run appropriate verification.
10. Report actual results.
11. Never claim unverified success.

If requirements are ambiguous or conflicting:

STOP and ask for clarification.

Do not guess.