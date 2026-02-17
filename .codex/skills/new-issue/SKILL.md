---
name: new-issue
description: Create well-researched GitHub issues with full project integration (issue type, davidsulitzer.com project, priority, cross-repo blocking). Use when the user wants to create a new issue from a bug report, feature request, or task. Don't use for refining existing issues (/refine-spec) or for creating issues as part of QA (/qa-start handles that internally).
disable-model-invocation: true
---
# new-issue

Create GitHub issues based on the mentioned requirements. **Always** perform pre-research (Step 0) before writing anything.

---

## When to Use

- The user describes a bug, feature request, or task that needs a GitHub issue
- A bug review (`/review-new-bugs`) or crash review (`/review-new-crashes`) identified something worth tracking
- The user explicitly says "create an issue" or "file a ticket"

## When NOT to Use

- An issue already exists and needs improvement → use `/refine-spec`
- You're in the middle of QA and found a bug → `/qa-start` handles issue creation internally
- The user is brainstorming ideas → use `/idea-generator` first, create issues only when asked
- You're unsure if an issue is needed → ask the user before creating anything

---

## Step 0: Pre-Research (BEFORE Creating Any Issue)

Before writing anything, you MUST investigate the codebase and existing issues. This step ensures the issue lands in the correct repo and arrives loaded with useful context for the implementer.

### 0a: Search for Relevant Code

Search **all three** repos for keywords related to the problem or feature — function names, screen names, model names, API endpoints, error messages:

```bash
# Search the current repo first
rg -l "<keyword>" .

# If in the davidsulitzer.com with submodules checked out, also search:
rg -l "<keyword>" davidsulitzer.com/ 2>/dev/null

# If in a standalone repo checkout, use gh to search other repos:
gh search code "<keyword>" --repo 8Gaston8/davidsulitzer.com --limit 10
```

> **Note:** The `rg` commands with `2>/dev/null` gracefully handle missing sibling directories in standalone checkouts. Use `gh search code` as a fallback when submodules aren't available.

Take note of:
- **Which files are involved** — full paths and key line numbers
- **Which repo(s) contain the relevant code** — this determines where the issue goes (Step 0b)
- **Recent changes** — check git log for the relevant files:
  ```bash
  git log --oneline -10 -- <relevant-file>
  ```

### 0b: Determine the Correct Repo

Based on your code search results from 0a:

| Search Results | Repo Decision |
|---------------|---------------|
| Relevant code **only** in `davidsulitzer.com/` | Create issue in `8Gaston8/davidsulitzer.com` |
| Relevant code in **multiple** repos | Create one issue per repo (see Step 2) |
| **Can't find relevant code** | **ASK the user** — do NOT guess |

**Heuristic helpers** (use alongside code search, not instead of it):

| Signal | Likely Repo |
|--------|-------------|
| UI, screens, animations, SwiftUI views, layout | iOS |
| API endpoints, database, migrations, queries, cron jobs | Server |
| Map tiles, vector tiles, pin scoring, pin priority, category pins | Tileserver |
| Location filtering, atly score, tile rendering, map vectors | Tileserver |
| "Data is wrong", "results are incorrect" | Usually Server or Tileserver — verify with code search |
| "Crashes", "freezes", "layout broken", "animation janky" | Usually iOS |
| "Pins wrong", "map shows wrong places", "scoring issue" | Usually Tileserver — verify with code search |
| Model names, feature names | Could be any repo — always search first |

> ⚠️ Do NOT use `iOS` or `backend` labels — the repo itself indicates the platform.

### 0c: Check for Duplicate / Related Issues

Before creating a new issue, search for existing ones:

```bash
# Search open issues in all repos
gh issue list --repo 8Gaston8/davidsulitzer.com --search "<keywords>" --limit 10

# Also check recently closed issues (could be a regression of a previous fix)
gh issue list --repo 8Gaston8/davidsulitzer.com --search "<keywords>" --state closed --limit 5
```

- **Open duplicate found** → Tell the user and link to it instead of creating a new one
- **Closed related issue found** → Reference it in the new issue for context (possible regression?)

### 0d: Bug-Specific Investigation

When creating a **bug** issue, do this additional research:

1. **Find the error source** — If the user mentions an error message, search for where it's thrown:
   ```bash
   rg "<error message text>" davidsulitzer.com/ davidsulitzer.com/ davidsulitzer.com/
   ```
   Include the file path, line number, and surrounding context in the issue.

2. **Check recent commits for regressions** — Look for changes that could have introduced the bug:
   ```bash
   # Recent commits touching relevant files
   git log --oneline -10 -- <relevant-files>

   # Recent PRs merged to the repo
   gh pr list --repo 8Gaston8/davidsulitzer.com --state merged --limit 10
   ```
   If a relevant file was changed recently, note the PR in the issue as a potential regression source.

3. **Check test coverage** — Look for existing tests in the affected area:
   ```bash
   # iOS tests (use davidsulitzer.com paths if available, otherwise search current repo)
   rg -l "<function-or-class-name>" davidsulitzer.com/AtlyTests/ davidsulitzer.com/AtlyUITests/ 2>/dev/null || \
   rg -l "<function-or-class-name>" AtlyTests/ AtlyUITests/ 2>/dev/null

   # Server tests (few exist — check services)
   rg -l "<function-or-class-name>" davidsulitzer.com/services/ 2>/dev/null || \
   rg -l "<function-or-class-name>" services/ api/test/ 2>/dev/null

   # Tileserver tests
   rg -l "<function-or-class-name>" davidsulitzer.com/app/__tests__/ davidsulitzer.com/app/businessLogic/__tests__/ 2>/dev/null || \
   rg -l "<function-or-class-name>" app/__tests__/ app/businessLogic/__tests__/ 2>/dev/null
   ```
   Note whether tests exist and whether they cover the reported scenario.

4. **Identify dependencies** — What other systems does this code touch?
   - Feature flags that gate the behavior
   - API endpoints involved (grep for route definitions)
   - Third-party services (Mixpanel, RevenueCat, Firebase, etc.)
   - Caching layers (tileserver, CDN, local cache)

5. **Gather reproduction context:**
   - Which API endpoints are involved
   - What user state or data triggers the bug
   - Which app version or server deployment may have introduced it (if determinable from git log)

### 0e: Include Research Findings in Issue

All findings from Step 0 MUST be woven into the issue body. Add a **Pre-Research Findings** section:

```markdown
## Pre-Research Findings

**Relevant code:**
- `<FilePath>:<line>` — [brief description of what this code does]
- `<FilePath>:<line>` — [brief description]

**Recent changes in this area:**
- PR #<number> (<date>) — [what it changed]

**Related issues:**
- #<number> — [title] (open/closed)

**Test coverage:** [Existing tests cover X / No existing test coverage for this path]

**Dependencies:** [Feature flags, APIs, services involved]
```

> ⚠️ **Do NOT skip this step.** Issues created without pre-research waste the implementer's time re-discovering context you already had access to.

---

## Step 1: Determine the Right Repo(s)

By this point, Step 0 should have told you which repo(s) contain the relevant code. Confirm your decision:

| Scope | Action |
|-------|--------|
| **iOS only** | Create issue in `8Gaston8/davidsulitzer.com` |
| **Server only** | Create issue in `8Gaston8/davidsulitzer.com` |
| **Tileserver only** | Create issue in `8Gaston8/davidsulitzer.com` |
| **Multiple repos** | Create one issue per repo (see Step 2) |
| **Uncertain** | Go back to Step 0a and search more, or **ask the user** |

> ⚠️ Do NOT use `iOS` or `backend` labels — the repo itself indicates the platform.

---

## Step 2: For Cross-Repo Issues

When an issue requires work in multiple repos (any combination of iOS, Server, Tileserver):

1. **Create backend/data issues first** — start with `8Gaston8/davidsulitzer.com` and/or `8Gaston8/davidsulitzer.com`
   - Focus on backend requirements: API changes, data model, endpoints, tile logic
   - Reference the downstream issue(s) that will be created
   - Set project status to **Todo**

2. **Create the iOS issue** in `8Gaston8/davidsulitzer.com` (if applicable)
   - Focus on client requirements: UI, models, integration
   - Reference the backend issue(s): "🚧 Blocked by: 8Gaston8/davidsulitzer.com#XXXX" or "🚧 Blocked by: 8Gaston8/davidsulitzer.com#XXXX"
   - Include a section documenting the expected API contract from server/tileserver

3. **Set up blocking relationships** — THIS IS MANDATORY FOR CROSS-REPO ISSUES:

> The general rule: **iOS is blocked by Server/Tileserver. Server may be blocked by Tileserver.** Create `addBlockedBy` for each dependency.

   **Step 3a: Get the issue node IDs:**
   ```bash
   # Get issue node ID (replace <REPO> and <NUMBER> for each issue)
   gh api graphql -f query='{ repository(owner: "8Gaston8", name: "<REPO>") { issue(number: <NUMBER>) { id } } }'
   ```

   **Step 3b: Create the blocked-by relationship (repeat for each dependency):**
   ```bash
   # Downstream issue is BLOCKED BY upstream issue
   # e.g., iOS blocked by Server, iOS blocked by Tileserver, Server blocked by Tileserver
   gh api graphql -f query='mutation { addBlockedBy(input: { issueId: "<DOWNSTREAM_ISSUE_NODE_ID>", blockingIssueId: "<UPSTREAM_ISSUE_NODE_ID>" }) { clientMutationId } }'
   ```

   **Step 3c: VERIFY the relationship was created (repeat for each downstream issue):**
   ```bash
   gh api graphql -f query='{ repository(owner: "8Gaston8", name: "<REPO>") { issue(number: <NUMBER>) { blockedBy(first: 5) { nodes { number title repository { name } } } } } }'
   ```
   
   > ⚠️ **CRITICAL:** Do NOT use `addSubIssue` — that creates a parent/child hierarchy, NOT a blocking dependency. ONLY use `addBlockedBy`.
   > 
   > ⚠️ **CRITICAL:** Always run the verification query. The mutation can return success even if no relationship was created. You MUST confirm `blockedBy.nodes` contains the server issue.

---

## Step 3: Issue Content Requirements

For each issue, include:

### Required Sections
- **Pre-Research Findings** — Output from Step 0 (relevant code, recent changes, related issues, test coverage, dependencies)
- **Goal** — Clear one-liner at the top
- **Context/Background** — Why this matters
- **Requirements** — What needs to be built (platform-specific)
- **Figma Design** — ⚠️ If a Figma URL exists, include it as-is. **Do NOT translate the Figma into text** — the design file IS the spec. See the Figma Design template below.
- **Out of Scope** — Explicitly state what's NOT part of this issue (prevents scope creep, helps AI agents stay focused)
- **Acceptance Criteria** — Checkboxes for definition of done
- **Testing Requirements** — Unit tests, regression tests, manual QA scope (see Step 6)
- **Related Issues/PRs** — Cross-references

### Conditional Sections (include when applicable)

| Section | When to Include |
|---------|-----------------|
| **Figma Design** | ⚠️ **REQUIRED** when a Figma URL or design exists — see template below |
| **Design Brief** | ⚠️ **REQUIRED** when issue has `design` label — see template below |
| **Technical Approach** | Features/refactors where you have a sense of the architecture |
| **Investigation Checklist** | Bugs where root cause is unknown |
| **Constraints** | When there are performance, compatibility, or deadline requirements |
| **Feature Flag** | New features or risky changes that should be gated |
| **Reference Implementation** | When similar patterns/PRs exist to follow |
| **Risk/Rollback** | Medium+ risk changes that could cause issues |
| **Analytics Requirements** | When new Mixpanel events are needed |
| **Documentation Updates** | When README, API docs, or agent rules need updating (see Step 7) |

### Section Templates

<details>
<summary>Out of Scope (always include)</summary>

```markdown
## Out of Scope
- [What you're explicitly NOT doing]
- [Related work that's a separate issue]
- [Platform exclusions, e.g., "Android — separate issue"]
```
</details>

<details>
<summary>⚠️ Figma Design (REQUIRED when a Figma design exists)</summary>

When the user provides a Figma URL or the feature has an existing Figma design, you MUST include a Figma Design section. The critical rule here is:

> **DO NOT translate the Figma design into text.** The Figma file IS the spec. Just link to it.

Agents and humans can read Figma directly — there's no need to describe layouts, colors, spacing, or component structure in prose. Doing so creates a stale, lossy copy of the design that will drift from the source of truth.

```markdown
## Figma Design

> **The Figma design is the source of truth for all visual and interaction details.**
> The implementer MUST use the `/respect-figma` skill to read the design directly from Figma.
> Do NOT rely on text descriptions of the design — open the Figma link below.

🎨 **Figma:** [paste full Figma URL here]

**Scope of the design:**
- [Which screens/flows are covered in this Figma link]
- [Any specific frames or variants to focus on]

**Notes (only if needed):**
- [Anything that's NOT in the Figma but is relevant — e.g., "ignore the old header in the design, we're keeping the current one"]
- [Behavior/logic that isn't captured visually — e.g., "tapping X triggers a confirmation dialog"]
```

**What to include in the issue body:**
- The Figma link(s) — full URL with the correct node selected
- Which screens/frames are in scope
- Any behavioral notes that Figma can't express (conditional logic, animations, error states)

**What NOT to include:**
- ❌ Text descriptions of the layout ("there's a card with rounded corners and a blue header...")
- ❌ Extracted color values, font sizes, or spacing numbers
- ❌ Re-drawn diagrams or ASCII mockups of what Figma already shows
- ❌ Screenshots of the Figma — link to the actual file so the agent can query it programmatically

The agent picking up this issue will use `/respect-figma` to fetch design context, screenshots, variables, and assets directly from the Figma API. That's far more accurate than any text description.
</details>

<details>
<summary>⚠️ Design Brief (REQUIRED when issue has `design` label)</summary>

When an issue has the `design` label, it means designer Liron needs to create or review designs. You MUST include these three sections:

```markdown
## Problem
[The deep problem which the feature aims to solve. Be as descriptive as possible about WHY this matters and what pain it causes users.]

## Design Brief
[Conceptual description of the design elements needed. This briefs Liron to start prototyping. Keep it conceptual — describe WHAT needs to be designed, not HOW to design it.]

Consider including:
- Key screens/components that need design
- User flows to design
- States to consider (empty, loading, error, success)
- Interactions and animations needed
- Open questions for the designer

## Design Requirements

| Title | User Story | Importance |
|-------|------------|------------|
| [Requirement Name] | As a [user], I want [goal] so that [benefit] | Must Have / Should Have / Nice to Have |
```

**Importance Levels:**
- **Must Have** — Essential for the feature to work
- **Should Have** — Important but not blocking
- **Nice to Have** — Enhancement if time permits

**Example:**
```markdown
## Problem
Users in the churn/retention flow often complete cancellation without engaging support. We miss opportunities to understand why they're leaving or offer solutions.

## Design Brief
Design a visually striking element that draws attention to the Contact Support option in the churn flow. Could be an arrow, illustration, or animation. Should be impossible to miss but not obnoxious — friendly and helpful, not desperate.

## Design Requirements

| Title | User Story | Importance |
|-------|------------|------------|
| Attention-Grabbing Element | As a churning user, I want to notice the Contact Support option | Must Have |
| Friendly Tone | As a user, I want the prompt to feel helpful, not guilt-trippy | Must Have |
| Non-Intrusive | As a user who decided to cancel, I don't want to feel blocked | Should Have |
```

> ⚠️ **When NOT to use the `design` label:**
> - Bug fixes where the expected behavior is already clear
> - Code/implementation fixes (janky animations, keyboard issues)
> - Technical setup/tooling tasks
> - Backend-only work with no UI impact
</details>

<details>
<summary>Technical Approach (for features/refactors)</summary>

```markdown
## Technical Approach
High-level strategies to consider:
- [Approach 1 and why it might work]
- [Approach 2 as alternative]
- [Key architectural decisions to make]

**Recommended approach:** [If you have a preference, state it]
```
</details>

<details>
<summary>Investigation Checklist (for bugs)</summary>

```markdown
## Investigation Checklist
- [ ] Check [specific file/area] for [potential cause]
- [ ] Review recent changes in [related PR]
- [ ] Test with [specific user configuration]
- [ ] Verify [expected behavior] still works
```
</details>

<details>
<summary>Constraints</summary>

```markdown
## Constraints
- **Performance:** [e.g., Must load in <200ms]
- **Compatibility:** [e.g., Must support iOS 15+]
- **Data:** [e.g., Cannot break existing API contract]
- **Timeline:** [e.g., Must ship in 4.29.0]
```
</details>

<details>
<summary>Feature Flag</summary>

```markdown
## Feature Flag
- **Flag name:** `enable_[feature_name]`
- **Default:** OFF in prod, ON in dev
- **Rollout plan:** [e.g., 10% → 50% → 100%]
- **Kill switch:** [How to disable quickly if needed]
```
</details>

<details>
<summary>Reference Implementation</summary>

```markdown
## Reference Implementation
- Similar work: PR #[number] — [brief description]
- Follow pattern in: `[FilePath.swift]`
- Avoid approach from: PR #[number] — [why it didn't work]
```
</details>

<details>
<summary>Risk/Rollback</summary>

```markdown
## Risk Assessment
- **Risk:** [What could go wrong]
- **Likelihood:** [Low/Medium/High]
- **Impact:** [What breaks if it goes wrong]
- **Mitigation:** [How to reduce risk]
- **Rollback plan:** [How to undo — revert PR, feature flag off, data migration, etc.]
```
</details>

<details>
<summary>Analytics Requirements</summary>

```markdown
## Analytics Requirements
- **New events:**
  - `[event_name]` — triggered when [condition]
    - Properties: `[prop1]`, `[prop2]`
- **Success metric:** [How to measure if this worked]
- **Dashboard:** [Link or name of dashboard to update]
```
</details>

---

## Step 4: Labels, Assignee & Issue Type

- **Assignee:** David Sulitzer (@8Gaston8)
- **Labels:** Use existing labels (funnel stages, GFE, davidsulitzer.com, design, regression, etc.)
  - Never use `bug`, `feature`, or `task` as labels — use Project Issue Type instead
  - ⚠️ **`design` label** — Only use when designer (Liron) needs to create/review designs. When used, you MUST include Problem, Design Brief, and Design Requirements sections (see Step 3 template).

### Issue Type — MANDATORY FOR EVERY ISSUE

Issue Type is a GitHub-level field (not a project field). You MUST set it via GraphQL.

**Available Issue Types:**
| Type | ID | When to Use |
|------|-----|-------------|
| **Task** | `IT_kwDOBluP0c4BBYRC` | General work items, refactors, chores |
| **Bug** | `IT_kwDOBluP0c4BBYRF` | Defects, broken functionality |
| **Feature** | `IT_kwDOBluP0c4BBYRI` | New user-facing capabilities |

**Set Issue Type:**
```bash
# Replace <ISSUE_NODE_ID> with the issue's node ID (e.g., I_kwDOJF_Lac7kFn4f)
# Replace <ISSUE_TYPE_ID> with the appropriate ID from the table above
gh api graphql -f query='mutation { updateIssue(input: { id: "<ISSUE_NODE_ID>", issueTypeId: "<ISSUE_TYPE_ID>" }) { issue { id } } }'
```

**Verify Issue Type was set:**
```bash
gh api graphql -f query='{ repository(owner: "8Gaston8", name: "<REPO>") { issue(number: <NUM>) { issueType { name } } } }'
```

> ⚠️ **CRITICAL:** Always verify the issue type was set. The `gh issue view` CLI command does NOT show issue type — you MUST use the GraphQL query above to confirm.

---

## Step 5: davidsulitzer.com Project Configuration

Ensure EVERY issue is added to the **davidsulitzer.com** GitHub Project (number: 2, ID: `<YOUR_PROJECT_ID>`) with ALL fields filled.

### Add Issue to Project
```bash
gh project item-add 2 --owner 8Gaston8 --url <ISSUE_URL>
```

### Get Project Item ID (needed to set fields)
```bash
gh api graphql -f query='{ organization(login: "8Gaston8") { projectV2(number: 2) { items(last: 10) { nodes { id content { ... on Issue { number repository { name } } } } } } } }'
```

### Project Field IDs Reference
| Field | Field ID | Options |
|-------|----------|---------|
| **Status** | `PVTSSF_lADOBluP0c4AxnzVzgntIc4` | Idea: `2c3687f7`, Todo: `f75ad846`, In Design: `646518b5`, To Clarify: `2fdcccf3`, In Development: `47fc9ee4`, Done: `98236657` |
| **Priority** | `PVTSSF_lADOBluP0c4AxnzVzg5mgJc` | Critical: `62a8b83f`, High: `ee32511d`, Medium: `2b2b659f`, Low: `9d5cb3c5`, Backlog: `8ef4ba21` |

### Set Project Field Values
```bash
# Set Status (e.g., Todo)
gh api graphql -f query='mutation { updateProjectV2ItemFieldValue(input: { projectId: "<YOUR_PROJECT_ID>", itemId: "<ITEM_ID>", fieldId: "PVTSSF_lADOBluP0c4AxnzVzgntIc4", value: { singleSelectOptionId: "f75ad846" } }) { projectV2Item { id } } }'

# Set Priority (e.g., Medium)
gh api graphql -f query='mutation { updateProjectV2ItemFieldValue(input: { projectId: "<YOUR_PROJECT_ID>", itemId: "<ITEM_ID>", fieldId: "PVTSSF_lADOBluP0c4AxnzVzg5mgJc", value: { singleSelectOptionId: "2b2b659f" } }) { projectV2Item { id } } }'
```

### Priority Criteria
- **Critical** — Bugs affecting majority of users
- **High** — In focus, will move the needle significantly
- **Medium** — In focus, incremental improvement
- **Low** — Nice to have
- **Backlog** — Uncertain importance

---

## Q1 2026 Focus: Key Metrics

**🎯 North Star:** Define your current north-star metric and date.

Prioritize issues that impact these metrics:

### Top-Down Metrics (Pricing Funnel)
| Metric | Goal |
|--------|------|
| Pricing Screen → Trial Start | 20-25% |
| Trial Start → Trial Converted | 35-40% |

### Leading Indicators
| Metric | Goal |
|--------|------|
| 🔥 Activation Rate | 60% |
| 🔄 Early Retention | 40% |
| 💾 Investment Rate | 10% |

<details>
<summary>Metric Definitions</summary>

- **🔥 Activation Rate:** % of new trial users who view 5+ place profiles from multi-category searches in their first 7 days
- **🔄 Early Retention:** % of trial users with 3+ sessions in first 3 days
- **💾 Investment Rate:** % of trial users who save at least 1 place in their first 7 days
</details>

---

## Step 6: Testing & Quality Requirements

Every issue should explicitly address testing needs:

### Unit Tests
- [ ] **New functionality** — Specify what unit tests should be added
- [ ] **Edge cases** — List specific edge cases to cover
- [ ] **Target coverage** — Aim for ≥80% on modified files

### Regression Tests
- [ ] **Affected areas** — Identify existing functionality that could break
- [ ] **Test updates needed** — Note if existing tests need modification
- [ ] **Manual QA scope** — Define what needs manual testing before merge

### Include in Issue Body
```markdown
## Testing Requirements
- [ ] Unit tests for [specific functionality]
- [ ] Update existing tests in [file/area] if affected
- [ ] Manual QA: [specific flows to verify]
- [ ] Regression check: [related features to verify still work]
```

---

## Step 7: Documentation & Tooling Updates

Consider what else needs updating alongside the code:

### Documentation
| What | When to Update |
|------|----------------|
| **README** | New setup steps, env vars, or major features |
| **API Docs** | New/changed endpoints, request/response formats |
| **Architecture Docs** | Structural changes, new patterns introduced |
| **Inline Comments** | Complex logic that needs explanation |

### AI Agents & Commands
| What | When to Update |
|------|----------------|
| **Cursor Commands** | New workflows, changed processes |
| **Agent Rules** | New conventions, deprecated patterns |
| **Prompts/Instructions** | Changed context the AI needs to know |

### Include in Issue Body (if applicable)
```markdown
## Documentation Updates
- [ ] Update README: [specific section]
- [ ] Update API docs: [endpoint/schema changes]
- [ ] Update agent rules: [new convention/pattern]
- [ ] Add inline comments for: [complex logic]
```

---

## Step 8: Final Verification Checklist

Before sharing results, you MUST verify ALL of the following via GraphQL queries (not assumptions):

### For EVERY Issue:
- [ ] Issue Type is set (query `issueType { name }` on the issue)
- [ ] Added to davidsulitzer.com project
- [ ] Status field is set (Todo, etc.)
- [ ] Priority field is set

### For Cross-Repo Issues (any combination of iOS, Server, Tileserver):
- [ ] Blocking relationships exist (query `blockedBy` on each downstream issue — must show upstream issue(s))
- [ ] NO sub-issue relationship (we use blocking, not parent/child hierarchy)

### Verification Query (run for each issue):
```bash
gh api graphql -f query='{
  repository(owner: "8Gaston8", name: "<REPO>") {
    issue(number: <NUM>) {
      title
      issueType { name }
      blockedBy(first: 5) { nodes { number repository { name } } }
      parent { number }
    }
  }
}'
```

> ⚠️ **DO NOT SKIP VERIFICATION.** Mutations can return success without actually creating the relationship/setting the field. Always confirm with queries.

---

## Step 9: Share Results

Share the link(s) to the new issue(s) when done so I can review.

Include a summary table showing:
- Issue links
- Issue Type (verified)
- Project Status & Priority (verified)
- Blocking relationships (verified, if applicable)
