# FIGMA IMPLEMENTATION SPECIFICATION
## AI Procurement & Purchase Approval System

### 1. Prototype Access Verification
- **URL:** https://www.figma.com/design/maPwEYOWc2ZHj4gP9w5uTV/Untitled?node-id=0-1&m=dev
- **Access Status:** SUCCESS. The prototype metadata and design context were successfully extracted via Figma API.

### 2. Screen List (Extracted from Prototype)
The prototype contains the following screens under the "AI Procurement Approval System – Screens" frame:
- **Purchase requests** (ID: 9:317)
- **New request (Flow A)** (ID: 9:645)
- **Draft request** (ID: 9:1006)
- **Edit draft request** (ID: 9:1237)
- **Submission error** (ID: 9:1563)
- **Approvals queue (Flow B)** (ID: 9:1813)
- **Approval + budget warning** (ID: 9:2010)
- **Edit locked (in approval)** (ID: 9:2321)
- **Budget review (Finance)** (ID: 9:2431)
- **Finance budget decision** (ID: 9:2635)
- **Revision required** (ID: 9:2928)
- **Edit after revision** (ID: 9:3179)
- **Rejected request** (ID: 9:3468)
- **Approved request** (ID: 9:3745)
- **Sourcing (Flow C)** (ID: 9:4001)
- **Collect quotation (upload)** (ID: 9:4163)
- **Comparison not ready yet** (ID: 9:4373)
- **Suppliers (Flow C)** (ID: 9:4479)
- **Comparison + expiry warning** (ID: 9:4790)
- **AI analysis + anomaly (Flow D)** (ID: 9:5291)

### 3. Design System & Tokens
**Layout & Spacing:**
- **Structure:** Sidebar navigation (256px width) on the left, main content area on the right.
- **Main Container:** Padding 32px.
- **Cards/Containers:** Border radius 8px, border width 0.667px (solid #e4e7ec), drop shadows.

**Typography:**
- **Font Family:** Inter (sans-serif)
- **Weights:** Regular (400), Medium (500), SemiBold (600)
- **Sizes:** Headings 24px, Subtitles 14px, Small text/Meta 11px/12px.

**Colors:**
- **Backgrounds:** App Background #f5f6f8 (light grey), Content Background #ffffff (white), Sidebar Background #ffffff.
- **Primary Action:** Blue #4a56d2.
- **Text:** Dark #12161c (Primary), Grey #5a6472 (Secondary), Light Grey #8a929e (Tertiary).
- **Status Badges:**
  - *Revision required / Budget warning:* Yellow (BG #fdf4e3, Border #f2ddad, Text #7a5209)
  - *Error / Rejected:* Red (BG #fdecec, Border #f4c2c2, Text #8e1e1e)
  - *Pending approval:* Light Blue (BG #eef1ff, Border #c3ccff, Text #2f3789)
  - *Approved:* Green (BG #e9f7ef, Border #b6e2c7, Text #16603b)
  - *Quotation comparison:* Muted Blue (BG #eaf3fb, Border #bcd8ef, Text #184e75)
  - *Draft / Closed:* Grey (BG #f5f6f8, Border #cdd2da, Text #5a6472)

### 4. Component Inventory
- **Sidebar Navigation:** Menu list with icons, badges for unread/action items, and user role indicator.
- **Tabs (Tablist):** "All", "In flight", "Needs me", "Sourcing", "Fulfilment", "Closed". Active tab uses blue background (#eef1ff).
- **Data Table / List View:** Columns for Request, Category, Estimated, Needed by, Status.
- **Alert Cards:** Prominent banners at the top of lists for urgent action (e.g. "Revision required", "Error").
- **Buttons:** Primary solid buttons (Blue), Secondary outline/text buttons.
- **Input Fields:** Search bar with left icon, Textareas for AI prompting (Start from a note).
- **Status Badges:** Rounded pills with custom colors depending on status.

### 5. Navigation Flow
- **Flow A (Employee):** Start -> New request (Draft) -> Input AI prompt -> Edit draft -> Submit -> Approval Queue.
- **Flow B (Manager/Finance):** Approvals queue -> View details -> See Budget warning -> Approve/Reject/Request Revision.
- **Flow C (Procurement):** Sourcing -> Suppliers -> Collect quotation (upload PDF).
- **Flow D (Procurement/AI):** AI analysis -> Anomaly detection -> Comparison view.

### 6. Gap Analysis: Prototype vs. Current Frontend Repo
| Component/Feature | Prototype (Figma) | Current Repo (rontend/src/App.tsx) | Gap Assessment |
| :--- | :--- | :--- | :--- |
| **Architecture** | Multi-screen flow (20 screens) with deep linking. | Single-page App (SPA) with 418 lines, no routing. | **CRITICAL:** Needs full routing implementation. |
| **Layout** | Sidebar + Main Content (App Shell pattern). | Simple center-aligned max-width 1200px container. | **HIGH:** Layout needs complete rewrite. |
| **Role Switching** | Integrated into authentication/session. | Simple dropdown at the top right for mock switching. | **HIGH:** Needs real auth context. |
| **Styling** | Utility classes / Tailwind CSS structure with precise Design Tokens. | Hardcoded inline styles (style={{...}}). | **CRITICAL:** Inline styles must be replaced. |
| **Typography** | Uses Inter with strict weight rules. | Default browser serif/sans-serif. | **MEDIUM:** Add font imports. |
| **Status Badges** | 6+ detailed visual variations (color matching). | 3 basic colors hardcoded in inline styles. | **MEDIUM:** Need Badge component. |
| **Tabs & Filtering** | "All", "In flight", "Needs me" filtering logic. | Lists all PRs straight down, no tabs. | **HIGH:** Missing UI and filtering logic. |
| **Alerts/Warnings** | Interactive alert cards at top of list. | Basic top banner (message state). | **LOW:** Easy to implement as components. |

### Conclusion
The current frontend is a low-fidelity "Proof of Concept" utilizing inline styles and a single-file architecture. The Figma prototype represents a high-fidelity, production-ready enterprise dashboard requiring a component-based architecture, routing, and a dedicated design system (CSS/Tailwind).

---
*Generated by AI Assistant based on Figma Prototype extraction.*
