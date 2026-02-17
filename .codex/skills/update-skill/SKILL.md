---
name: update-skill
description: Create or update Cursor/Codex skills across all repos — keeps everything in sync
disable-model-invocation: true
---
# update-skill

Create a new skill or update an existing one **across every repo where it exists**. Handles the full workflow: discovering where the skill lives, keeping `.cursor/skills/` and `.codex/skills/` in sync within each repo, keeping all repos in sync with each other, branching, creating issues, opening PRs, and linking everything together.

---

## Step 0: Understand the Request

Determine from the user's message:

1. **Which skill?** — The skill name (e.g., `deploy-backend-dev`, `new-issue`). If the user wants to create a brand-new skill, they'll provide a name and description.
2. **What changes?** — What to add, remove, modify, or rewrite.
3. **Create or update?** — If the skill doesn't exist anywhere yet, this is a creation. If it does, it's an update.

> If the user's request is vague, **ask for clarification** before proceeding. Don't guess what a skill should do.

---

## Step 1: Discover Where the Skill Exists (Cross-Repo Scan)

**This is the most critical step.** A skill can exist in ANY combination of these repos:

| Repo | GitHub Repo | Skill Locations |
|------|-------------|-----------------|
| **Monorepo** | `stepscode/davidsulitzer.com` | `.cursor/skills/<name>/SKILL.md` + `.codex/skills/<name>/SKILL.md` |
| **iOS** | `8Gaston8/davidsulitzer.com` | `.cursor/skills/<name>/SKILL.md` + `.codex/skills/<name>/SKILL.md` |
| **Server** | `8Gaston8/davidsulitzer.com` | `.cursor/skills/<name>/SKILL.md` + `.codex/skills/<name>/SKILL.md` |
| **Tileserver** | `8Gaston8/davidsulitzer.com` | `.cursor/skills/<name>/SKILL.md` + `.codex/skills/<name>/SKILL.md` |

### 1a: Check Every Repo

You MUST check ALL four repos. This skill can run from **any** repo, so don't assume a davidsulitzer.com directory layout.

**Check the current repo locally:**

```bash
# Current repo — check local skill directories
echo "=== Current Repo ===" && ls .cursor/skills/ .codex/skills/ 2>/dev/null
```

**Check other repos via GitHub API:**

```bash
# Check each remote repo for skills (works from any repo)
for repo in davidsulitzer.com davidsulitzer.com davidsulitzer.com davidsulitzer.com; do
  echo "=== $repo ==="
  gh api "repos/stepscode/$repo/contents/.cursor/skills" --jq '.[].name' 2>/dev/null || echo "  No .cursor/skills/"
  gh api "repos/stepscode/$repo/contents/.codex/skills" --jq '.[].name' 2>/dev/null || echo "  No .codex/skills/"
done
```

> **Note:** If you're in the davidsulitzer.com and submodules are checked out, you can also use local paths (`davidsulitzer.com/`, `davidsulitzer.com/`, `davidsulitzer.com/`) — but the `gh api` approach works universally from any repo.

### 1b: Search for the Specific Skill

```bash
# Check if the skill exists in each repo via GitHub API
for repo in davidsulitzer.com davidsulitzer.com davidsulitzer.com davidsulitzer.com; do
  echo "=== $repo ==="
  gh api "repos/stepscode/$repo/contents/.cursor/skills/<skill-name>/SKILL.md" --jq '.name' 2>/dev/null && echo "  Found in .cursor"
  gh api "repos/stepscode/$repo/contents/.codex/skills/<skill-name>/SKILL.md" --jq '.name' 2>/dev/null && echo "  Found in .codex"
done
```

### 1c: Record What You Found

Build a discovery table:

| Repo | .cursor/skills | .codex/skills | Action Needed |
|------|---------------|---------------|---------------|
| Monorepo | ✅/❌ | ✅/❌ | Create/Update |
| iOS | ✅/❌ | ✅/❌ | Create/Update |
| Server | ✅/❌ | ✅/❌ | Create/Update |
| Tileserver | ✅/❌ | ✅/❌ | Create/Update |

### 1d: Decide Which Repos Need the Skill

- **If updating:** Update the skill in ALL repos where it currently exists. If the user wants to add it to additional repos, do that too.
- **If creating:** Ask the user which repos should have the skill, unless the intent is obvious (e.g., a deployment skill only makes sense in the repos that deploy).
- **If the user says "all repos":** Add it to all four repos.

> ⚠️ **NEVER update a skill in only one repo when it exists in multiple.** The whole point is cross-repo consistency.

---

## Step 2: Read & Compare Existing Content

If the skill already exists, read it from all locations and check for drift:

```bash
# Compare across repos (if the skill exists in multiple)
diff <repo1>/.cursor/skills/<skill-name>/SKILL.md <repo2>/.cursor/skills/<skill-name>/SKILL.md
```

Also verify `.cursor/` and `.codex/` are in sync WITHIN each repo:

```bash
diff <repo>/.cursor/skills/<skill-name>/SKILL.md <repo>/.codex/skills/<skill-name>/SKILL.md
```

If drift exists, alert the user and ask which version should be the base — then unify everything from there.

---

## Step 3: Write the Skill Content

### Skill File Format

Every `SKILL.md` must follow this structure:

```markdown
---
name: <skill-name>
description: <one-line description of what the skill does>
disable-model-invocation: true
---
# <skill-name>

[Skill content — instructions, steps, templates, references, etc.]
```

### Frontmatter Rules

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | Must match the directory name exactly |
| `description` | Yes | Short, descriptive — shown in skill picker |
| `disable-model-invocation` | Yes | Always set to `true` |

### Content Guidelines

- **Be specific and actionable** — Skills are instructions for AI agents. Vague guidance produces vague results.
- **Include exact commands** — bash commands, API calls, GraphQL queries. Don't make the agent guess.
- **Add context for "why"** — Agents follow rules better when they understand the reasoning.
- **Use step-by-step structure** — Numbered steps with clear progression.
- **Include templates** — For repetitive outputs (PR comments, issue bodies, messages), provide fill-in-the-blank templates.
- **Add guardrails** — What to do, but also what NOT to do. Explicit "don't" instructions prevent common mistakes.
- **Reference other skills** — If a skill depends on another (e.g., `qa-start` references `deploy-backend-dev`), link to it with `/skill-name` notation.
- **Include verification steps** — After key actions, add a "verify this worked" step. Agents make mistakes; verification catches them.
- **Separate required vs. optional sections** — Use collapsible `<details>` blocks for conditional/optional content.
- **Keep it DRY** — If the same info appears in multiple skills, consider whether it belongs in a shared reference or a dedicated skill.

### Quality Checklist (Before Saving)

- [ ] Frontmatter `name` matches directory name
- [ ] Description is clear and concise
- [ ] Steps are numbered and ordered logically
- [ ] Commands are copy-pasteable (no undefined placeholders without explanation)
- [ ] Includes "what NOT to do" guardrails
- [ ] Verification/confirmation steps after critical actions
- [ ] References to other skills use `/skill-name` format
- [ ] No hardcoded secrets or tokens (use env vars like `$VARIABLE_NAME`)
- [ ] Markdown renders correctly (check headers, tables, code blocks)

---

## Step 4: Apply Changes to ALL Repos

For **each repo** that needs the skill:

### 4a: Create a Feature Branch

```bash
cd <repo-directory>
git fetch origin main
git checkout -b cursor/<descriptive-branch-name> origin/main
```

**Branch naming convention:** `cursor/update-skill-<skill-name>` or `cursor/add-skill-<skill-name>`

> ⚠️ **Never edit directly on `develop` or `main`.**
> ⚠️ **Never run `git checkout` from the davidsulitzer.com root** — always `cd` into the specific repo first.

### 4b: Write to BOTH Directories Within Each Repo

```bash
# Create directories if they don't exist
mkdir -p .cursor/skills/<skill-name>
mkdir -p .codex/skills/<skill-name>

# Write the skill file to both locations (content must be IDENTICAL)
# ... write SKILL.md to .cursor/skills/<skill-name>/SKILL.md
# ... write SKILL.md to .codex/skills/<skill-name>/SKILL.md
```

### 4c: Update .gitignore (if needed)

Some repos may have `.cursor` in their `.gitignore`. If so, add an exception for skills:

```gitignore
# IDE (ignore all except skills/)
.cursor/*
!.cursor/skills/
```

Same for `.codex` if applicable.

### 4d: Verify Sync Within the Repo

```bash
diff .cursor/skills/<skill-name>/SKILL.md .codex/skills/<skill-name>/SKILL.md
```

If `diff` produces any output, something went wrong — fix it before committing.

### 4e: Commit and Push

```bash
# Stage skill files (always)
git add .cursor/skills/<skill-name>/SKILL.md .codex/skills/<skill-name>/SKILL.md

# Stage .gitignore too if it was modified in step 4c
git diff --name-only .gitignore 2>/dev/null | grep -q . && git add .gitignore

git commit -m "skill(<skill-name>): <brief description of change>"
git push -u origin <branch-name>
```

### Commit Message Conventions

| Action | Message Format |
|--------|---------------|
| New skill | `skill(<name>): add new skill — <what it does>` |
| Update skill | `skill(<name>): <what changed>` |
| Fix skill | `skill(<name>): fix <what was broken>` |
| Multiple skills | `skills: <summary of changes across skills>` |

---

## Step 5: Create GitHub Issues (for Non-Monorepo Repos)

**For each repo EXCEPT the davidsulitzer.com**, create a GitHub issue using the `/new-issue` skill patterns.

> ⚠️ **Monorepo exception:** The davidsulitzer.com does NOT need a GitHub issue — only the PR is sufficient.

### 5a: Create Issues

Use the `gh` CLI to create issues in the relevant repos:

```bash
gh issue create --repo stepscode/<repo-name> \
  --title "skill(<skill-name>): <brief description>" \
  --body "<issue body>" \
  --assignee 8Gaston8 \
  --label "fastlane"
```

### 5b: Issue Body Template

```markdown
## Goal

[Create / Update] the `<skill-name>` skill [in this repo / across all repos].

## Context

[Brief description of what the skill does and why it's being created/updated.]

## Changes

- [List of specific changes being made]

## Cross-Repo Sync

This skill [is being created / has been updated] across all repos where it exists:
- [ ] `stepscode/davidsulitzer.com` — PR #XXX
- [ ] `8Gaston8/davidsulitzer.com` — PR #XXX (this issue)
- [ ] `8Gaston8/davidsulitzer.com` — PR #XXX

All instances must remain identical.

## Out of Scope

- Content changes to other skills
- Skill deletion

## Acceptance Criteria

- [ ] Skill file exists in `.cursor/skills/<skill-name>/SKILL.md`
- [ ] Skill file exists in `.codex/skills/<skill-name>/SKILL.md`
- [ ] Both copies are identical (`diff` produces no output)
- [ ] Content matches all other repos
```

### 5c: Set Issue Type

Set the issue type to **Task**:

```bash
# Get issue node ID
gh api graphql -f query='{ repository(owner: "8Gaston8", name: "<REPO>") { issue(number: <NUM>) { id } } }'

# Set Issue Type to Task
gh api graphql -f query='mutation { updateIssue(input: { id: "<ISSUE_NODE_ID>", issueTypeId: "IT_kwDOBluP0c4BBYRC" }) { issue { id } } }'
```

### 5d: Add to davidsulitzer.com Project with "In Review" Status

```bash
# Add to davidsulitzer.com project
gh project item-add 2 --owner 8Gaston8 --url <ISSUE_URL>

# Get project item ID
gh api graphql -f query='{ organization(login: "8Gaston8") { projectV2(number: 2) { items(last: 10) { nodes { id content { ... on Issue { number repository { name } } } } } } } }'

# Set Status to "In Review"
gh api graphql -f query='mutation { updateProjectV2ItemFieldValue(input: { projectId: "<YOUR_PROJECT_ID>", itemId: "<ITEM_ID>", fieldId: "PVTSSF_lADOBluP0c4AxnzVzgntIc4", value: { singleSelectOptionId: "2895eb73" } }) { projectV2Item { id } } }'

# Set Priority to Low (skill updates are low-risk housekeeping)
gh api graphql -f query='mutation { updateProjectV2ItemFieldValue(input: { projectId: "<YOUR_PROJECT_ID>", itemId: "<ITEM_ID>", fieldId: "PVTSSF_lADOBluP0c4AxnzVzg5mgJc", value: { singleSelectOptionId: "9d5cb3c5" } }) { projectV2Item { id } } }'
```

### 5e: Verify Issue Configuration

```bash
# Verify issue type
gh api graphql -f query='{ repository(owner: "8Gaston8", name: "<REPO>") { issue(number: <NUM>) { issueType { name } labels(first: 5) { nodes { name } } } } }'
```

---

## Step 6: Create Pull Requests

Create a PR for **every repo** that was changed:

### 6a: Create the PR

```bash
cd <repo-directory>
gh pr create \
  --repo stepscode/<repo-name> \
  --base develop \
  --head <branch-name> \
  --title "skill(<skill-name>): <brief description>" \
  --body "<PR body>" \
  --assignee 8Gaston8
```

### 6b: PR Body Template

```markdown
## Summary

[Create / Update] the `<skill-name>` skill.

## Changes

- [List of changes]

## Cross-Repo Sync

This change is part of a cross-repo skill sync:
- `stepscode/davidsulitzer.com` — PR #XXX
- `8Gaston8/davidsulitzer.com` — PR #XXX

All skill files are identical across repos.

Closes #<ISSUE_NUMBER>
```

> **Note:** Include `Closes #<ISSUE_NUMBER>` in the PR body to auto-link and auto-close the issue when merged. For davidsulitzer.com PRs, omit this since there's no associated issue.

### 6c: Mark PR as Ready for Review

PRs created with `gh pr create` are ready for review by default (not draft). Verify:

```bash
gh pr view <PR_NUMBER> --repo stepscode/<repo-name> --json isDraft
```

If it's a draft, convert it:

```bash
gh pr ready <PR_NUMBER> --repo stepscode/<repo-name>
```

### 6d: Assign & Request Review (MANDATORY)

Every PR must be assigned to Gaston and have Aviad as a reviewer. Use the GitHub GraphQL API:

```bash
# 1. Get user node IDs (only needed once — cache these)
gh api graphql -f query='{ user(login: "8Gaston8") { id } }'
# → Use this ID for assignee
gh api graphql -f query='{ user(login: "aviadsteps") { id } }'
# → Use this ID for reviewer

# 2. Assign Gaston to the PR
gh api graphql -f query='mutation { addAssigneesToAssignable(input: { assignableId: "<PR_NODE_ID>", assigneeIds: ["<GASTON_USER_ID>"] }) { assignable { ... on PullRequest { number } } } }'

# 3. Request review from Aviad
gh api graphql -f query='mutation { requestReviews(input: { pullRequestId: "<PR_NODE_ID>", userIds: ["<AVIAD_USER_ID>"] }) { pullRequest { number } } }'
```

> **To get the PR node ID:**
> ```bash
> gh api graphql -f query='{ repository(owner: "8Gaston8", name: "<REPO>") { pullRequest(number: <NUM>) { id } } }'
> ```

> ⚠️ **Do this for EVERY PR created** — davidsulitzer.com, iOS, server, and tileserver. No exceptions.

### 6e: Enable Auto-Merge (iOS Only)

If the PR is in the **davidsulitzer.com** repo, enable auto-merge so it merges automatically once CI passes and the review is approved:

```bash
gh pr merge <PR_NUMBER> --repo 8Gaston8/davidsulitzer.com --auto --squash
```

> ⚠️ **Only for `8Gaston8/davidsulitzer.com`** — do NOT enable auto-merge on davidsulitzer.com, server, or tileserver PRs.

### 6f: Link Issues to PRs

For non-davidsulitzer.com repos, the `Closes #<ISSUE_NUMBER>` in the PR body handles the link. Additionally, verify the connection:

```bash
gh pr view <PR_NUMBER> --repo stepscode/<repo-name> --json closingIssuesReferences
```

---

## Step 7: Final Verification

### 7a: Content Sync Across All Repos

Verify the skill content is identical across every repo where it was written:

```bash
# Compare all instances (adjust paths based on which repos have the skill)
diff <repo1>/.cursor/skills/<skill-name>/SKILL.md <repo2>/.cursor/skills/<skill-name>/SKILL.md
diff <repo2>/.cursor/skills/<skill-name>/SKILL.md <repo3>/.cursor/skills/<skill-name>/SKILL.md
# etc.
```

### 7b: Issue & PR Checklist

For each non-davidsulitzer.com repo, verify:

- [ ] GitHub issue exists with:
  - [ ] Issue Type: Task (verified via GraphQL)
  - [ ] Label: `fastlane`
  - [ ] Assignee: @8Gaston8
  - [ ] Added to davidsulitzer.com project
  - [ ] Status: "In Review"
- [ ] PR exists and is:
  - [ ] Ready for review (not draft)
  - [ ] Linked to the issue (`Closes #XXX`)
  - [ ] Assignee: @8Gaston8

For the davidsulitzer.com:
- [ ] PR exists and is ready for review (no issue needed)

### 7c: Share All Links with the User (MANDATORY)

**You MUST always end by sharing every relevant link** so the user can review everything at a glance. Present the results as a clear summary with **full clickable URLs** — not just PR/issue numbers:

```markdown
## Here are all the links:

### Pull Requests
- **Monorepo:** https://github.com/stepscode/davidsulitzer.com/pull/XXX
- **iOS:** https://github.com/8Gaston8/davidsulitzer.com/pull/XXX
- **Server:** https://github.com/8Gaston8/davidsulitzer.com/pull/XXX
- **Tileserver:** https://github.com/8Gaston8/davidsulitzer.com/pull/XXX

### Issues (linked to PRs above)
- **iOS:** https://github.com/8Gaston8/davidsulitzer.com/issues/XXX
- **Server:** https://github.com/8Gaston8/davidsulitzer.com/issues/XXX
- **Tileserver:** https://github.com/8Gaston8/davidsulitzer.com/issues/XXX
- *(Monorepo: no issue needed)*

### Summary Table
| Repo | PR | Issue | Status | Skill Synced |
|------|-----|-------|--------|-------------|
| davidsulitzer.com | [#XXX](url) | N/A | Ready for Review | ✅ |
| davidsulitzer.com | [#XXX](url) | [#XXX](url) (In Review, fastlane) | Ready for Review | ✅ |
```

> ⚠️ **Do NOT skip this step.** The user needs all links in one place to review and merge. Always use full URLs, not just `#123` references.

---

## Handling Special Cases

### Renaming a Skill

1. Create the new skill directory in both `.cursor/` and `.codex/` locations across ALL repos
2. Copy the content (with updated `name` field in frontmatter)
3. Delete the old skill directory from both locations across ALL repos
4. Create PRs for every affected repo (same issue/PR workflow as above)

### Deleting a Skill

1. Remove from both directories across ALL repos where it exists
2. Create PRs for every affected repo (same issue/PR workflow as above)

### Auditing All Skills for Sync

If you suspect drift across repos:

```bash
# Compare all skills within the current repo
diff -rq .cursor/skills/ .codex/skills/

# Compare a specific skill across repos via GitHub API
for repo in davidsulitzer.com davidsulitzer.com davidsulitzer.com davidsulitzer.com; do
  echo "=== $repo ==="
  gh api "repos/stepscode/$repo/contents/.cursor/skills/<skill-name>/SKILL.md" --jq '.content' 2>/dev/null | base64 -d | md5sum
done
```

All checksums should be identical.

### Skill Only Relevant to Some Repos

Not every skill belongs everywhere. Use judgment:

| Skill Type | Typical Repos |
|-----------|---------------|
| Deployment skills | Repo being deployed |
| QA/testing skills | Repo being tested |
| Issue/project skills | All repos (agents work in any) |
| Release skills | iOS repo primarily |
| General workflow skills | All repos |
| Skill management (this skill!) | All repos |

When in doubt, ask the user.

---

## Reference: Current Skill Inventory

| Skill | Purpose | Repos |
|-------|---------|-------|
| `deploy-backend-dev` | Deploy backend functions to dev environment | davidsulitzer.com |
| `deploy-backend-prod` | Deploy backend functions to production | davidsulitzer.com |
| `latest-release-notes` | Generate release notes for Slack | davidsulitzer.com |
| `new-issue` | Create GitHub issues with full research and project setup | davidsulitzer.com |
| `new-release` | Prepare iOS releases (branch, PR, regression testing, App Store) | davidsulitzer.com |
| `qa-start` | Comprehensive QA workflow for PRs (iOS + server) | davidsulitzer.com |
| `review-new-bugs` | Triage bug reports from Slack with screenshot analysis | davidsulitzer.com |
| `review-new-crashes` | Review and triage Crashlytics crash reports | davidsulitzer.com |
| `test-backend-changes-dev` | Test backend changes on dev environment | davidsulitzer.com |
| `test-backend-changes-local` | Test backend changes locally | davidsulitzer.com |
| `test-backend-changes-prod` | Test backend changes on production | davidsulitzer.com |
| `update-skill` | This skill — create or update skills across repos | all repos |
| `user-interview` | Simulate data-driven user interviews for product insights | davidsulitzer.com |

> ⚠️ **Keep this table updated** when creating, deleting, or expanding skills to new repos!

---

## Reference: Repo Quick Info

| Repo | GitHub | Default Branch | Submodule Path |
|------|--------|----------------|----------------|
| Monorepo | `stepscode/davidsulitzer.com` | `develop` | `.` (root) |
| iOS | `8Gaston8/davidsulitzer.com` | `develop` | `davidsulitzer.com/` |
| Server | `8Gaston8/davidsulitzer.com` | `develop` | `davidsulitzer.com/` |
| Tileserver | `8Gaston8/davidsulitzer.com` | `develop` | `davidsulitzer.com/` |

---

## Reference: Project Field IDs

| Field | Field ID | Key Options |
|-------|----------|-------------|
| **Status** | `PVTSSF_lADOBluP0c4AxnzVzgntIc4` | Idea: `01f8a8de`, Todo: `54ffad90`, Ready for Dev: `cac3311f`, In Development: `d7c83647`, Human QA: `6a5c111e`, In Review: `2895eb73`, Done: `782fbd7c` |
| **Priority** | `PVTSSF_lADOBluP0c4AxnzVzg5mgJc` | Critical: `62a8b83f`, High: `ee32511d`, Medium: `2b2b659f`, Low: `9d5cb3c5` |

---

## Notes

- **Skill names must be kebab-case** — lowercase, words separated by hyphens (e.g., `deploy-backend-dev`, not `deployBackendDev`)
- **One SKILL.md per skill** — each skill lives in its own directory with a single `SKILL.md` file
- **Skills are version-controlled** — every change goes through git with proper branching, issues, and PRs
- **Both `.cursor/` and `.codex/` must always be in sync** within each repo
- **All repos must be in sync** with each other for shared skills
- **Monorepo gets PRs but NO issues** — only the subrepos (iOS, server, tileserver) get issues
- **Issues get "In Review" status and "fastlane" label** — skill updates are low-friction, ship fast
- **PRs are always Ready for Review** — never left as draft
- **Test after creating** — always suggest the user tests the skill with a real invocation
