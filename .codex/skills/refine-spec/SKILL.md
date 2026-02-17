---
name: refine-spec
description: Refine and improve an existing GitHub issue's spec through codebase research, edge case analysis, and iterative PM discussion.
disable-model-invocation: true
---
# refine-spec

Take an existing GitHub issue and elevate its spec to production-ready quality. This skill guides you through codebase research, section compliance (per the `/new-issue` skill), edge case discovery, and iterative refinement with the PM — so the AI agent or developer who picks it up makes zero mistakes.

---

## When to Use

- A spec exists but feels thin, vague, or missing context
- A design decision was just made and needs to be baked into the spec
- The PM wants to stress-test edge cases before handing off to development
- An issue was created quickly and now needs the full `/new-issue` treatment
- The spec drifted after discussion and needs to be reconciled with decisions made

---

## Step 0: Read the Issue

### 0a: Fetch the Full Issue

```bash
gh issue view <NUMBER> --repo stepscode/<REPO> --json title,body,labels,assignees,state,milestone
```

Take note of:
- **Labels** — especially `design` (triggers mandatory Design Brief sections) and `fastlane`
- **Milestone** — context for prioritization
- **Current body** — what's already there vs what's missing

### 0b: Identify What the User Wants to Change

Ask yourself:
1. Is this a **full rewrite** or **targeted improvements**?
2. Did the PM make specific design decisions that need to be captured?
3. Are there new requirements, constraints, or scope changes?
4. Is the PM asking for edge case analysis?

> If the user's request is vague (e.g., "make this spec better"), ask what aspect they want improved: completeness, clarity, edge cases, technical depth, or all of the above.

---

## Step 1: Pre-Research the Codebase

Before changing a single word, investigate the codebase. This is the same research from `/new-issue` Step 0 — but applied to an existing issue that may have skipped this step.

### 1a: Search for Relevant Code

Search **all repos** for keywords related to the feature/bug:

```bash
# 1. Always search the current repo first
rg -l "<keyword>" .

# 2. If in the davidsulitzer.com with submodules checked out, also search sibling repos:
rg -l "<keyword>" davidsulitzer.com/ 2>/dev/null

# 3. If in a standalone repo checkout (sibling dirs won't exist), use GitHub API:
gh search code "<keyword>" --repo 8Gaston8/davidsulitzer.com --limit 10
```

> **Note:** The `2>/dev/null` suppresses errors when sibling directories don't exist (standalone checkouts). Always search `.` first so you never miss the current repo's code.

**Capture for each relevant file:**
- Full path and key line numbers
- What the code does (brief description)
- How it relates to the feature being specified

### 1b: Check Recent Changes

```bash
git log --oneline -10 -- <relevant-files>
```

Note any recent PRs that touched the area — they may contain context or introduce constraints.

### 1c: Check for Related Issues

```bash
# Open issues
gh issue list --repo stepscode/<REPO> --search "<keywords>" --limit 10

# Recently closed (possible regression context)
gh issue list --repo stepscode/<REPO> --search "<keywords>" --state closed --limit 5
```

### 1d: Check Test Coverage

```bash
# iOS tests
rg -l "<function-or-class-name>" davidsulitzer.com/AtlyTests/ 2>/dev/null

# Server tests
rg -l "<function-or-class-name>" davidsulitzer.com/api/test/ 2>/dev/null
```

### 1e: Identify Dependencies

Look for:
- Feature flags that gate the behavior
- API endpoints involved (grep for route definitions)
- Third-party services (analytics, RevenueCat, Firebase, etc.)
- Caching layers
- Cross-repo dependencies (iOS ↔ Server ↔ Tileserver)

> ⚠️ **Do NOT skip pre-research.** Even if the issue already has some code references, they may be outdated or incomplete. Fresh research catches drift.

---

## Step 2: Audit Sections Against the `/new-issue` Skill

Compare the existing issue body against the required and conditional sections from `/new-issue` Step 3. Build a gap table:

### Required Sections (MUST exist in every issue)

| Section | Present? | Notes |
|---------|----------|-------|
| **Pre-Research Findings** | ✅/❌ | Code refs, recent changes, related issues, test coverage, dependencies |
| **Goal** | ✅/❌ | Clear one-liner |
| **Context/Background** | ✅/❌ | Why this matters |
| **Requirements** | ✅/❌ | What needs to be built |
| **Out of Scope** | ✅/❌ | What's NOT part of this issue |
| **Acceptance Criteria** | ✅/❌ | Checkboxes for definition of done |
| **Testing Requirements** | ✅/❌ | Unit tests, regression, manual QA |
| **Related Issues/PRs** | ✅/❌ | Cross-references |

### Conditional Sections (include when applicable)

| Section | Applicable? | Present? | Notes |
|---------|------------|----------|-------|
| **Problem + Design Brief + Design Requirements** | Only if `design` label | ✅/❌ | ⚠️ REQUIRED when `design` label is present |
| **Technical Approach** | Features/refactors | ✅/❌ | Architecture, files to change |
| **Constraints** | Performance/compat/deadline | ✅/❌ | |
| **Feature Flag** | New features, risky changes | ✅/❌ | |
| **Reference Implementation** | Similar patterns exist | ✅/❌ | |
| **Risk/Rollback** | Medium+ risk changes | ✅/❌ | |
| **Analytics Requirements** | New analytics events | ✅/❌ | |
| **Documentation Updates** | README, API docs, agent rules | ✅/❌ | |

> Present this gap table to the PM. Let them decide which missing sections are relevant before you start writing.

---

## Step 3: Analyze Edge Cases

This is where specs go from "good" to "bulletproof." For every feature in the spec, systematically think through:

### 3a: State Transitions

- What are all the possible states? (e.g., loading, active, inactive, error, empty)
- What triggers each transition?
- Can the user get stuck in an unexpected state?
- What happens on state reset (new session, navigation, app restart)?

### 3b: Interaction Combinations

- What happens when this feature interacts with other features in the same area?
- If there's a toggle/filter, does it survive navigation, back-button, other selections?
- What about concurrent actions (rapid tapping, network in flight)?

### 3c: Data Edge Cases

- What if the data is empty? (No results, no items, no content)
- What if the data is missing fields? (Null/undefined values from API)
- What if the data is stale? (Cached, outdated, timezone mismatch)
- What about pagination? Does the feature work across pages?

### 3d: UI Edge Cases

- What about different sheet/modal states? (Minimized, expanded, transitioning)
- What about transient states? (Search focused, autocomplete showing, animations in progress)
- Dark mode? Dynamic Type? VoiceOver?
- Does it work when related UI elements are hidden/empty?

### 3e: Platform Edge Cases

- App backgrounding and foregrounding
- App kill and restart
- Network errors mid-action
- Low connectivity / timeout scenarios

### 3f: Present Edge Cases to the PM

**Do NOT silently make decisions about edge cases.** Present them as a table:

| Scenario | Question / Suggested Behavior |
|----------|-------------------------------|
| [Edge case 1] | [What should happen? / Here's what I suggest: ...] |
| [Edge case 2] | [What should happen? / Here's what I suggest: ...] |

Let the PM confirm or override each one before writing them into the spec.

> **The goal is to eliminate ambiguity.** Every edge case that's undocumented is a coin-flip for the implementer. Document the decision, even if the decision is "we don't handle this — it's out of scope."

---

## Step 4: Draft the Updated Spec

### 4a: Preserve What's Good

Don't rewrite sections that are already solid. Only modify what needs improvement.

### 4b: Add Missing Sections

Fill in every gap identified in Step 2, using the templates from `/new-issue` Step 3.

### 4c: Weave in Edge Cases

Edge cases should NOT be a standalone dump. Integrate them:
- **Behavioral edge cases** → Add to an "Edge Cases & Clarifications" table
- **Empty/error states** → Add to the relevant spec section (e.g., "Empty State" subsection)
- **State management edge cases** → Add to the "State Management" or "Toggle Behavior" section
- **Testing edge cases** → Add to "Testing Requirements" as specific test cases

### 4d: Add Pre-Research Findings

If the original spec lacked code references, add the **Pre-Research Findings** section with:
- Relevant file paths + line numbers + brief descriptions
- Recent changes (PRs that touched the area)
- Related issues (open and closed)
- Test coverage status
- Dependencies (APIs, feature flags, services)

### 4e: Ensure Technical Approach is Implementation-Ready

The Technical Approach section should give the implementer a clear roadmap:
- **Files to change** — with specific descriptions of what changes in each file
- **Key implementation notes** — gotchas, caveats, patterns to follow or avoid
- **Recommended approach** — if there are multiple valid approaches, state which one and why

---

## Step 5: Update the Issue

### 5a: Apply the Changes

```bash
gh issue edit <NUMBER> --repo stepscode/<REPO> --body "$(cat <<'EOF'
<full updated issue body>
EOF
)"
```

> ⚠️ **This replaces the entire body.** Always include ALL sections — both unchanged and updated — in the new body. Never use `--body-file` with partial content.

### 5b: Labels — Do NOT Remove

> ⚠️ **NEVER remove existing labels during spec refinement.** Labels like `design` are kept permanently on the issue — they indicate the issue *involves* design work, not that design is pending. Even if the design decision has been made, the label stays.

You may **add** labels if the refinement reveals they're needed (e.g., adding `fastlane`):

```bash
gh issue edit <NUMBER> --repo stepscode/<REPO> --add-label "fastlane"
```

### 5c: Do NOT Update Project Status During Refinement

> ⚠️ **Do NOT change the project status at any point during spec refinement.** Regardless of what status the issue was in when the conversation started, leave it as-is until the PM explicitly confirms the spec is finalized.

**Only when the PM gives final approval** (e.g., "looks good, this is ready"), update the status to **Ready for Dev**:

```bash
# Get project item ID via the issue itself (avoids the last-N item window problem)
gh api graphql -f query='{ repository(owner: "8Gaston8", name: "<REPO>") { issue(number: <NUMBER>) { projectItems(first: 5) { nodes { id project { title } } } } } }' --jq '.data.repository.issue.projectItems.nodes[] | select(.project.title == "davidsulitzer.com") | .id'

# Move to "Ready for Dev" — ONLY after PM final approval
gh api graphql -f query='mutation { updateProjectV2ItemFieldValue(input: { projectId: "<YOUR_PROJECT_ID>", itemId: "<ITEM_ID>", fieldId: "PVTSSF_lADOBluP0c4AxnzVzgntIc4", value: { singleSelectOptionId: "cac3311f" } }) { projectV2Item { id } } }'
```

> **Note:** We query `projectItems` on the issue itself rather than scanning the last N project items. This works regardless of how many items are in the project.

---

## Step 6: Iterate with the PM

Spec refinement is rarely one-shot. After the first update:

### 6a: Summarize What Changed

Tell the PM exactly what you added, removed, or modified — in plain language, not diffs.

### 6b: Flag Open Questions

If any edge cases or design decisions are still unresolved, list them explicitly:

> **Still need your input on:**
> 1. [Question about behavior X]
> 2. [Question about scope Y]
> 3. [Question about edge case Z]

### 6c: Apply Follow-Up Changes

When the PM responds with decisions:
1. Update the spec immediately
2. Summarize what changed in this iteration
3. Repeat until the PM is satisfied

> **Keep iterating.** A spec is done when the PM says it's done, not when you think it's complete.

---

## Step 7: Final Quality Check

Before declaring the spec done, verify:

### Content Quality
- [ ] Every section from Step 2's gap table is addressed (present or explicitly N/A)
- [ ] Edge cases are documented with clear expected behaviors
- [ ] Technical approach references specific file paths and line numbers
- [ ] Acceptance criteria are concrete and testable (not vague)
- [ ] Testing requirements include unit tests, regression tests, AND manual QA
- [ ] Out of scope is explicit (prevents scope creep during implementation)

### Issue Metadata
- [ ] Labels are unchanged (never remove existing labels — especially `design`)
- [ ] Milestone is set
- [ ] Assignee is set
- [ ] Issue type is set (Feature / Bug / Task)
- [ ] Project status is unchanged (only update to "Ready for Dev" after PM gives explicit final approval)

### Readability
- [ ] A developer or AI agent reading this spec for the first time can implement the feature without asking clarifying questions
- [ ] No contradictions between sections
- [ ] No placeholder text or TODOs left in the body
- [ ] Tables are formatted correctly (render check)

---

## Anti-Patterns (What NOT to Do)

| Anti-Pattern | Why It's Bad | Do This Instead |
|-------------|-------------|-----------------|
| Rewriting the entire spec without reading it first | Loses context and decisions already made | Read first, preserve what's good |
| Making design decisions without asking the PM | You're refining, not designing | Present options, let PM decide |
| Dumping edge cases without suggested behaviors | Shifts the thinking burden to the implementer | Always include a suggested behavior |
| Adding sections just to check a box | Bloats the spec with low-value content | Only add sections that provide real value |
| Ignoring the `design` label requirements | The `/new-issue` skill REQUIRES Problem + Design Brief + Design Requirements when `design` label is present | Check labels first, comply with the section requirements |
| Removing labels during refinement | Labels are permanent markers — `design` means the issue involves design, not that design is pending | Never remove labels; only add if needed |
| Updating project status without PM approval | Only the PM decides when a spec is ready for development | Leave status unchanged until PM explicitly says "ready" |
| Updating the spec without telling the PM what changed | PM can't review what they can't see | Always summarize changes after each update |
| Skipping pre-research because "the issue already has context" | Existing context may be outdated or incomplete | Always do fresh research |
| Writing vague acceptance criteria | "Works correctly" is not testable | Be specific: "When X happens, Y should result" |

---

## Quick Reference: Relationship to Other Skills

| Skill | Relationship |
|-------|-------------|
| `/new-issue` | `refine-spec` applies `/new-issue`'s section requirements to an EXISTING issue. If the issue was created without `/new-issue`, this skill brings it up to standard. |
| `/qa-start` | A well-refined spec makes QA faster. The testing requirements section feeds directly into QA checklists. |
| `/update-skill` | If the refinement process reveals a gap in any skill (including this one), use `/update-skill` to improve it. |
