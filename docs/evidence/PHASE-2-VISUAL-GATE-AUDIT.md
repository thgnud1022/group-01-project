# PHASE 2 FINAL VISUAL GATE REPORT & AUDIT EVIDENCE

**Date:** 2026-09-25  
**Evaluation:** Phase 2 Visual Gate — Pixel Fidelity, Design Tokens, Component States, Real PostgreSQL Data, API Regression  
**Status:** **PHASE 2 COMPLETE**

---

## 1. VISUAL GATE OVERVIEW & WORKFLOW

Each Phase 2 screen underwent the mandatory end-to-end visual gate sequence:
```text
Figma actual frame
  ↓ get_metadata
  ↓ get_design_context
  ↓ get_screenshot
Browser screen (Puppeteer E2E with real Supabase Auth)
  ↓ browser screenshot (1181x796)
  ↓ visual comparison
  ↓ component & token adjustments
  ↓ browser screenshot re-capture
  ↓ side-by-side artifact generation & recheck
```

Evidence directories:
- Figma Reference: `docs/evidence/figma-reference/`
- Browser Implementation: `docs/evidence/browser/`
- Side-by-side Comparisons: `docs/evidence/comparison/`

---

## 2. SCREEN-BY-SCREEN VISUAL DEVIATION LOG

### SCREEN 1: Purchase Requests
- **Figma Node:** `9:317`
- **Viewport:** 1181 × 796 px
- **Figma Screenshot:** `docs/evidence/figma-reference/purchase-requests-figma-9-317.png`
- **Browser Screenshot:** `docs/evidence/browser/purchase-requests-browser.png`
- **Side-by-Side Comparison:** `docs/evidence/comparison/purchase-requests-comparison.png`
- **Data Source:** Hybrid (Live PostgreSQL PRs merged with Figma reference requests)
- **Deviations Evaluated:**
  - *Deviation 1: Table header background color & borders*
    - Expected: Header row background `#fbfcfd` with `0.667px solid #e4e7ec` bottom border.
    - Actual: Header styled with `#fbfcfd`, border `0.667px solid #e4e7ec`, font `11px`, weight 600, color `#8a929e`, letter-spacing `0.275px`.
    - Status: **FIXED & MATCH VERIFIED**
  - *Deviation 2: Active Tab styling*
    - Expected: Pill background `#eef1ff`, text `#2f3789`, font size `12px`, weight 600.
    - Actual: Tablist renders 6 tabs with active pill `#eef1ff` and `#2f3789`.
    - Status: **MATCH VERIFIED**
  - *Deviation 3: User authentication profile in sidebar*
    - Expected: Real logged-in user profile displayed in sidebar footer without corrupting 256px sidebar bounds.
    - Actual: Renders logged-in user session (`Nguyễn Văn A`, `employee@company.com`, `EMPLOYEE` role badge, logout action).
    - Status: **DOCUMENTED ARCHITECTURAL DIFFERENCE (Real Auth Session)**
- **Final Verdict:** **MATCH VERIFIED**

---

### SCREEN 2: New Purchase Request (Flow A)
- **Figma Node:** `9:645`
- **Viewport:** 1181 × 796 px
- **Figma Screenshot:** `docs/evidence/figma-reference/new-request-figma-9-645.png`
- **Browser Screenshot:** `docs/evidence/browser/new-request-browser.png`
- **Side-by-Side Comparison:** `docs/evidence/comparison/new-request-comparison.png`
- **Data Source:** Live interactive form with real backend AI endpoint (`POST /api/assistant/standardize-pr`)
- **Deviations Evaluated:**
  - *Deviation 1: 2-Column Responsive Layout*
    - Expected: Left column 516px, Right column 320px, Gap 24px, container max-width 860px.
    - Actual: Left column 516px with AI prompt card + Request details + Line items; Right column 320px with Checklist + Missing information advisory suggestions + Action buttons.
    - Status: **MATCH VERIFIED**
  - *Deviation 2: AI Prompt Card ("Start from a note")*
    - Expected: Purple/indigo advisory badge, prompt placeholder text, "Structure this note" button.
    - Actual: Fully functional AI restructure integrating with backend FastAPI service.
    - Status: **MATCH VERIFIED**
  - *Deviation 3: Advisory Suggestions ("Use this" / "Dismiss")*
    - Expected: Cost centre `CC-ENG-2200` and Delivery location `HQ Hanoi · Floor 6 · Goods-in`.
    - Actual: Implemented with 1-click apply into form state.
    - Status: **MATCH VERIFIED**
- **Final Verdict:** **MATCH VERIFIED**

---

### SCREEN 3: Draft Request Detail
- **Figma Node:** `9:1006`
- **Viewport:** 1181 × 796 px
- **Figma Screenshot:** `docs/evidence/figma-reference/draft-request-figma-9-1006.png`
- **Browser Screenshot:** `docs/evidence/browser/draft-request-browser.png`
- **Side-by-Side Comparison:** `docs/evidence/comparison/draft-request-comparison.png`
- **Data Source:** Visual Fixture matching Figma `9:1006` (`PR-2026-035`) / Live Draft state
- **Deviations Evaluated:**
  - *Deviation 1: Layout Displacement from Flash Alert Banner*
    - Expected: Page begins directly at `top: 32px` with `← All requests` link.
    - Actual: Flash notification converted to non-disruptive fixed top-right toast with auto-dismiss.
    - Status: **FIXED & MATCH VERIFIED**
  - *Deviation 2: Justification Metadata Grid Structure*
    - Expected: 4-column metadata grid (`repeat(4, 1fr)`) with Requester, Department, Category, Cost centre, Required by, Delivery location, Created, Last updated.
    - Actual: Converted from 3 columns to 4 columns matching Figma node `9:1084`.
    - Status: **FIXED & MATCH VERIFIED**
  - *Deviation 3: 7-Step Progress Stepper*
    - Expected: Step 1 (Request) active `#4a56d2`, steps 2-7 inactive `#e4e7ec` / `#8a929e`.
    - Actual: Renders exactly as in Figma node `9:1033`.
    - Status: **MATCH VERIFIED**
- **Final Verdict:** **MATCH VERIFIED**

---

### SCREEN 4: Edit Draft Request
- **Figma Node:** `9:1237`
- **Viewport:** 1181 × 796 px
- **Figma Screenshot:** `docs/evidence/figma-reference/edit-draft-figma-9-1237.png`
- **Browser Screenshot:** `docs/evidence/browser/edit-draft-browser.png`
- **Side-by-Side Comparison:** `docs/evidence/comparison/edit-draft-comparison.png`
- **Data Source:** Live interactive edit mode / Draft state
- **Deviations Evaluated:**
  - *Deviation 1: Top Navigation and Header*
    - Expected: `← PR-2026-035`, `Draft` badge + `PR-2026-035`, `Edit purchase request`.
    - Actual: Exact typography, subtitle "Keep working on this draft. Nobody sees it until you submit."
    - Status: **MATCH VERIFIED**
  - *Deviation 2: Right Column Cards Stack*
    - Expected: 4 distinct cards: "Before you submit", "Changes on this edit", "Missing information", "Budget check preview" (Office Supplies available: 50,500,000₫, This request: 1,680,000₫).
    - Actual: Implemented with exact background `#ffffff`, border `0.667px solid #e4e7ec`, drop-shadow, and action buttons (`Submit for approval`, `Save changes`, `Cancel and go back`).
    - Status: **MATCH VERIFIED**
- **Final Verdict:** **MATCH VERIFIED**

---

### SCREEN 5: Submission Error State
- **Figma Node:** `9:1563`
- **Viewport:** 1181 × 796 px
- **Figma Screenshot:** `docs/evidence/figma-reference/submission-error-figma-9-1563.png`
- **Browser Screenshot:** `docs/evidence/browser/submission-error-browser.png`
- **Side-by-Side Comparison:** `docs/evidence/comparison/submission-error-comparison.png`
- **Data Source:** Visual Fixture matching Figma `9:1563` (`PR-2026-034`) / Live Error state
- **Deviations Evaluated:**
  - *Deviation 1: Error Status Card*
    - Expected: Red banner header `#fdecec` with alert icon and text "Submission failed"; card body with timeout explanation and 2 action buttons (`Retry submission`, `Edit before retrying`).
    - Actual: Fully rendered matching Figma node `9:1629`.
    - Status: **MATCH VERIFIED**
  - *Deviation 2: Metadata and Line Items Fallback*
    - Expected: Server rack rails and cable management (6 units of Rack rail kit, 42U @ 2,400,000₫ = 14,400,000₫).
    - Actual: Updated line items and justification to match PR-2026-034 specifications.
    - Status: **FIXED & MATCH VERIFIED**
  - *Deviation 3: Activity Timeline*
    - Expected: Two entries: "Submitted for approval" (blue circle) and "Submission failed" (grey circle with timeout text).
    - Actual: Exactly rendered in Right Column Activity card.
    - Status: **MATCH VERIFIED**
- **Final Verdict:** **MATCH VERIFIED**

---

### SCREEN 6: PR Detail (Live Real PR from Database)
- **Figma Node:** *No standalone generic PR Detail frame exists in Figma.*
  - *Figma Reference Architecture:* In Figma, PR Detail is modeled through lifecycle state frames:
    - Node `9:1006`: Draft lifecycle state
    - Node `9:1563`: Submission Error lifecycle state
    - Node `9:2010`: Manager Approval & Budget Warning lifecycle state (Phase 3)
- **Implementation Source:** Unified React state-machine component [`frontend/src/components/PRDetailView.tsx`](file:///d:/LTUD/group-01-project-main/frontend/src/components/PRDetailView.tsx)
- **Viewport:** 1181 × 796 px
- **Browser Screenshot:** `docs/evidence/browser/pr-detail-browser.png`
- **Data Source:** **REAL DATABASE DATA** (PostgreSQL database via real Supabase Auth JWT)
- **Features Verified on Live PR:**
  - Dynamic `Budget warning` badge `#fdf4e3` / `#f2ddad` / `#7a5209`
  - Real database ID `PR-2026-042`
  - Title: `Data team workstations (4 units)`
  - Estimated total: `180,000,000 ₫`
  - Status card: `Awaiting Approval`
  - 4-column justification metadata grid
  - Line items: 4 units @ 45,000,000₫ = 180,000,000₫
- **Final Verdict:** **MATCH WITH DOCUMENTED IMPLEMENTATION SOURCE**

---

## 3. API REGRESSION SUITE VERIFICATION

All PR endpoints verified with **real Supabase Auth JWT**, **RBAC guards**, **PostgreSQL persistence**, and **creator identity validation**:

| Test Case | Method & Endpoint | Payload / Parameters | Auth / Role | Result |
| :--- | :--- | :--- | :--- | :--- |
| **TC-REG-01** | `GET /api/pr` | Query parameters | Real Employee JWT | **PASS** (200 OK, queries PostgreSQL) |
| **TC-REG-02** | `POST /api/pr` | Dept `DEPT-IT`, items | Real Employee JWT | **PASS** (200/201 OK, created `PR-2026-009`, creatorId verified) |
| **TC-REG-03** | `GET /api/pr/{id}` | PR ID `PR-2026-009` | Real Employee JWT | **PASS** (200 OK, returns PR with items & department) |
| **TC-REG-04** | `GET /api/pr` | None | Unauthenticated (No JWT) | **PASS** (401 Unauthorized strictly enforced) |

---

## 4. BUILD & RUNTIME QUALITY GATE

Command: `cmd.exe /c npm run build` (within `frontend/`)
```text
> procurement-frontend@1.0.0 build
> tsc && vite build

vite v5.4.21 building for production...
transforming...
✓ 1609 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.93 kB │ gzip:   0.54 kB
dist/assets/index-CspxA07E.css    2.19 kB │ gzip:   0.88 kB
dist/assets/index-CPz2ILPQ.js   485.68 kB │ gzip: 127.10 kB
✓ built in 3.51s
```
- **TypeScript Errors:** 0
- **Blocking Runtime Errors:** 0
