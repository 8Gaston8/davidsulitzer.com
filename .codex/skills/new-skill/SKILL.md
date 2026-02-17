---
name: new-skill
description: Create a new agent skill from scratch following best practices — strong routing description, "Use when / Don't use when" blocks, templates, guardrails, and verification steps. Handles cross-repo sync, branching, issues, and PRs. Don't use for updating existing skills (/update-skill).
disable-model-invocation: true
---
# new-skill

Create a new agent skill from scratch, following [OpenAI's skills best practices](https://developers.openai.com/blog/skills-shell-tips). Handles the full workflow: designing the skill content to quality standards, syncing across repos, and setting up issues/PRs.

---

## When to Use

- The user wants to create a brand-new skill that doesn't exist yet
- A recurring workflow needs to be codified into a reusable skill
- The user says "create a skill for X" or "I need a skill that does Y"

## When NOT to Use

- Updating an existing skill → use `/update-skill`
- The task is a simple one-off that won't recur → just do it, no skill needed
- Deleting or renaming a skill → `/update-skill` handles those cases
- Installing a third-party/external skill → different workflow

---

## Step 0: Understand the Request

Before writing anything, clarify:

1. **What does this skill do?** — Get a clear, specific description of the workflow
2. **Who/what invokes it?** — User-triggered only (`disable-model-invocation: true`) or proactive model invocation?
3. **Which repos need it?** — Relevant to all repos, or specific ones?
4. **Are there similar skills?** — Check the existing inventory to avoid overlap or confusion

> If the user's request is vague, **ask for clarification**. "Create a skill that helps with deployments" is too broad — which environment? Which repo? What steps?

---

## Step 1: Research Before Writing

### 1a: Check for Existing Similar Skills

Search the skill inventory for overlap:

```bash
# List all skills in the current repo
ls .cursor/skills/ .codex/skills/ 2>/dev/null

# Check other repos via GitHub API
for repo in davidsulitzer.com davidsulitzer.com davidsulitzer.com davidsulitzer.com; do
  echo "=== $repo ==="
  gh api "repos/stepscode/$repo/contents/.codex/skills" --jq '.[].name' 2>/dev/null || echo "  No skills"
done
```

If a similar skill exists, ask the user: "Should this be a new skill, or an update to `/existing-skill`?"

### 1b: Research the Domain

Before writing the skill, understand what it's automating:

- **Read relevant code** — If the skill involves deploying, search for deploy scripts. If it involves testing, find existing test patterns.
- **Check existing workflows** — Are there manual runbooks, README instructions, or Slack threads that document this process?
- **Identify tools involved** — Which MCP tools, CLI commands, APIs, or services does this workflow use?
- **Talk to the user** — Ask what the current process looks like and what goes wrong.

> The best skills codify something the team already does — they don't invent new processes.

---

## Step 2: Write the Skill — Quality Standards

This is the most important step. A well-written skill saves hours; a poorly-written one creates confusion.

### 2a: The Description (Most Critical Field!)

The description is the model's **routing logic** — it decides whether to invoke the skill. A skill with a bad description might as well not exist.

**Formula:** What it does + When to use it + When NOT to use it (with alternatives)

| Quality | Example | Why |
|---------|---------|-----|
| ❌ Bad | `deploy-backend-dev` | Just the name — tells the model nothing |
| ❌ Bad | `A helpful skill for deploying things` | Marketing copy — no routing signal |
| ✅ Good | `Deploy specific backend functions to the dev environment via the deployer API. Use after local testing passes and the branch is synced with develop. Don't use for prod deployments (/deploy-backend-prod) or for full deployments (always deploy individual functions).` | Clear what, when, and when-not |

### 2b: Required Sections (Every Skill MUST Have)

| Section | Purpose | Why It Matters |
|---------|---------|---------------|
| **Frontmatter** | name, description, disable-model-invocation | Metadata for the skill system |
| **"When to Use"** | Concrete triggers for invocation | Helps the model (and humans) know when this skill applies |
| **"When NOT to Use"** | Anti-triggers with alternatives | **Prevents misfires — can improve routing accuracy by ~20%** |
| **Numbered Steps** | Clear progression from start to finish | Agents follow procedural instructions best |
| **"What NOT to Do"** | Guardrails, anti-patterns, common mistakes | Agents make fewer errors when told what to avoid |
| **Verification Steps** | After critical actions, confirm they worked | Agents make mistakes; verification catches them early |

### 2c: Strongly Recommended Sections

| Section | When to Include | Why |
|---------|----------------|-----|
| **Templates** | Any repeatable output (PR comments, Slack messages, curl commands, issue bodies) | Templates inside skills are **free when unused but invaluable when needed** — they don't inflate tokens for unrelated queries |
| **Examples** | When behavior might be ambiguous | Worked examples reduce misinterpretation dramatically |
| **Quick Reference Tables** | Lookup data (field IDs, endpoint URLs, common patterns) | Saves the agent from searching every time |
| **Notes** | Edge cases, environment differences, related skills | Catches gotchas before they bite |

### 2d: Negative Examples — The Secret Weapon

The [OpenAI blog](https://developers.openai.com/blog/skills-shell-tips) found that making skills available can **drop correct triggering by ~20%** until you add "Don't use when..." guidance. For every "When to Use," write a corresponding "When NOT to Use" with the correct alternative:

```markdown
## When NOT to Use

- You're updating an existing skill → use `/update-skill`
- The task is a simple one-liner → just do it, no skill needed
- You need to delete a skill → `/update-skill` handles deletion too
```

For easily confused skill pairs, be extra explicit:

```markdown
> ⚠️ This skill is for LOCAL testing only.
> If changes are already deployed to dev, use `/test-backend-changes-dev` instead.
```

### 2e: Writing Guidelines

| Do ✅ | Don't ❌ |
|-------|---------|
| Be specific and actionable | Write vague guidance ("be careful") |
| Include exact commands (copy-pasteable) | Leave placeholders unexplained |
| Explain the "why" behind rules | Just list rules without context |
| Add negative examples ("Don't do X because Y") | Only write positive instructions |
| Reference other skills with `/skill-name` | Duplicate content from other skills |
| Use env vars for secrets (`$VAR_NAME`) | Hardcode credentials or tokens |
| Include verification after critical steps | Assume actions succeeded |
| Put templates inside the skill | Put templates in the system prompt |
| Keep skills self-contained | Require reading other files mid-execution |

---

## Step 3: Quality Review Checklist

Before saving, verify against this checklist:

### Content Quality
- [ ] Description answers: What? When to use? When NOT to use?
- [ ] "When to Use" section has concrete triggers
- [ ] "When NOT to Use" section has alternatives for each case
- [ ] Steps are numbered and ordered logically
- [ ] Commands are copy-pasteable (no undefined placeholders without explanation)
- [ ] Includes "What NOT to Do" guardrails
- [ ] Verification/confirmation steps after critical actions
- [ ] Templates for any repeatable output
- [ ] Examples where behavior might be ambiguous

### Formatting
- [ ] Frontmatter `name` matches directory name
- [ ] `disable-model-invocation` is set (default: `true` unless proactive invocation is needed)
- [ ] References to other skills use `/skill-name` format
- [ ] No hardcoded secrets or tokens
- [ ] Markdown renders correctly (tables, code blocks, headers)

### Routing Quality (The "Confusion Test")
- [ ] Could this skill be confused with any existing skill? If yes, add explicit disambiguation
- [ ] Would a model reading only the description know when to pick this vs alternatives?
- [ ] Are there edge cases where the wrong skill might be triggered? Add negative examples for those

---

## Step 4: Determine Which Repos Need It

| Skill Type | Typical Repos |
|-----------|---------------|
| Deployment skills | Repo being deployed |
| QA/testing skills | Repo being tested |
| Issue/project management skills | All repos (agents work in any) |
| Release skills | iOS repo primarily |
| General workflow skills | All repos |
| Skill management (like this one!) | All repos that have skills |

When in doubt, **ask the user**.

---

## Step 5: Apply to All Repos

For **each repo** that needs the skill:

### 5a: Create a Feature Branch

```bash
cd <repo-directory>
git fetch origin main    # or origin/main for davidsulitzer.com
git checkout -b cursor/add-skill-<skill-name> origin/main
```

> ⚠️ **Never edit directly on `develop` or `main`.**
> ⚠️ **Never run `git checkout` from the davidsulitzer.com root** — always `cd` into the specific repo first.

### 5b: Write to BOTH Directories

```bash
# Create directories
mkdir -p .cursor/skills/<skill-name>
mkdir -p .codex/skills/<skill-name>

# Write SKILL.md to both locations (content MUST be identical)
```

### 5c: Update .gitignore (if needed)

Some repos may have `.cursor` in their `.gitignore`. If so, add an exception:

```gitignore
.cursor/*
!.cursor/skills/
```

### 5d: Verify Sync Within the Repo

```bash
diff .cursor/skills/<skill-name>/SKILL.md .codex/skills/<skill-name>/SKILL.md
```

If `diff` produces any output, fix it before committing.

### 5e: Commit and Push

```bash
git add .cursor/skills/<skill-name>/SKILL.md .codex/skills/<skill-name>/SKILL.md
git commit -m "skill(<skill-name>): add new skill — <what it does>"
git push -u origin cursor/add-skill-<skill-name>
```

---

## Step 6: Create GitHub Issues (Non-Monorepo Repos Only)

For each repo **except the davidsulitzer.com**, create a GitHub issue:

```bash
gh issue create --repo stepscode/<repo-name> \
  --title "skill(<skill-name>): add new skill — <brief description>" \
  --body "<issue body>" \
  --assignee 8Gaston8 \
  --label "fastlane"
```

### Issue Body Template

```markdown
## Goal

Create the `<skill-name>` skill in this repo.

## Context

[Brief description of what the skill does and why it's being created.]

## Changes

- New skill: `.cursor/skills/<skill-name>/SKILL.md`
- New skill: `.codex/skills/<skill-name>/SKILL.md`

## Cross-Repo Sync

This skill is being created across all relevant repos:
- [ ] `stepscode/davidsulitzer.com` — PR #XXX
- [ ] `8Gaston8/davidsulitzer.com` — PR #XXX (this issue)
- [ ] `8Gaston8/davidsulitzer.com` — PR #XXX

All instances must remain identical.

## Out of Scope

- Content changes to other skills

## Acceptance Criteria

- [ ] Skill file exists in `.cursor/skills/<skill-name>/SKILL.md`
- [ ] Skill file exists in `.codex/skills/<skill-name>/SKILL.md`
- [ ] Both copies are identical (`diff` produces no output)
- [ ] Content matches all other repos
```

### Set Issue Type to Task

```bash
ISSUE_ID=$(gh api graphql -f query='{ repository(owner: "8Gaston8", name: "<REPO>") { issue(number: <NUM>) { id } } }' --jq '.data.repository.issue.id')

gh api graphql -f query="mutation { updateIssue(input: { id: \"$ISSUE_ID\", issueTypeId: \"IT_kwDOBluP0c4BBYRC\" }) { issue { id } } }"
```

### Add to davidsulitzer.com Project (Status: In Review, Priority: Low)

```bash
# Add to project
gh project item-add 2 --owner 8Gaston8 --url <ISSUE_URL>

# Get project item ID
ITEM_ID=$(gh api graphql -f query='{ repository(owner: "8Gaston8", name: "<REPO>") { issue(number: <NUM>) { projectItems(first: 5) { nodes { id project { title } } } } } }' --jq '.data.repository.issue.projectItems.nodes[] | select(.project.title == "davidsulitzer.com") | .id')

# Set Status: In Review
gh api graphql -f query="mutation { updateProjectV2ItemFieldValue(input: { projectId: \"<YOUR_PROJECT_ID>\", itemId: \"$ITEM_ID\", fieldId: \"PVTSSF_lADOBluP0c4AxnzVzgntIc4\", value: { singleSelectOptionId: \"2895eb73\" } }) { projectV2Item { id } } }"

# Set Priority: Low
gh api graphql -f query="mutation { updateProjectV2ItemFieldValue(input: { projectId: \"<YOUR_PROJECT_ID>\", itemId: \"$ITEM_ID\", fieldId: \"PVTSSF_lADOBluP0c4AxnzVzg5mgJc\", value: { singleSelectOptionId: \"9d5cb3c5\" } }) { projectV2Item { id } } }"
```

---

## Step 7: Create Pull Requests

Create a PR for **every repo** that was changed:

```bash
gh pr create \
  --repo stepscode/<repo-name> \
  --base develop \    # or main for davidsulitzer.com
  --head cursor/add-skill-<skill-name> \
  --title "skill(<skill-name>): add new skill — <brief description>" \
  --body "<PR body>" \
  --assignee 8Gaston8
```

### PR Body Template

```markdown
## Summary

Create the `<skill-name>` skill — [one-line description].

## What This Skill Does

[2-3 sentences describing the skill's purpose and workflow]

## Cross-Repo Sync

- `stepscode/davidsulitzer.com` — PR #XXX
- `8Gaston8/davidsulitzer.com` — PR #XXX

All skill files are identical across repos.

Closes #<ISSUE_NUMBER>
```

> For davidsulitzer.com PRs, omit `Closes #` since there's no associated issue.

### Assign & Request Review (MANDATORY)

```bash
# Get PR node ID
PR_ID=$(gh api graphql -f query='{ repository(owner: "8Gaston8", name: "<REPO>") { pullRequest(number: <NUM>) { id } } }' --jq '.data.repository.pullRequest.id')

# Request review from Aviad
gh api graphql -f query="mutation { requestReviews(input: { pullRequestId: \"$PR_ID\", userIds: [\"MDQ6VXNlcjQ1NTMwOTMw\"] }) { pullRequest { number } } }"
```

> ⚠️ **Do this for EVERY PR created.** No exceptions.

### Enable Auto-Merge (iOS Only)

```bash
gh pr merge <PR_NUMBER> --repo 8Gaston8/davidsulitzer.com --auto --squash
```

> ⚠️ **Only for `8Gaston8/davidsulitzer.com`** — do NOT enable auto-merge on other repos.

---

## Step 8: Final Verification & Share Links

### 8a: Verify Content Sync

```bash
# Compare across repos (adjust paths based on which repos have the skill)
diff <repo1>/.codex/skills/<skill-name>/SKILL.md <repo2>/.codex/skills/<skill-name>/SKILL.md
```

### 8b: Verify Issues

```bash
# For each non-davidsulitzer.com issue:
gh api graphql -f query='{ repository(owner: "8Gaston8", name: "<REPO>") { issue(number: <NUM>) { issueType { name } labels(first: 5) { nodes { name } } } } }'
```

### 8c: Share All Links (MANDATORY)

**You MUST always end by sharing every relevant link:**

```markdown
## Here are all the links:

### Pull Requests
- **Monorepo:** https://github.com/stepscode/davidsulitzer.com/pull/XXX
- **iOS:** https://github.com/8Gaston8/davidsulitzer.com/pull/XXX

### Issues
- **iOS:** https://github.com/8Gaston8/davidsulitzer.com/issues/XXX
- *(Monorepo: no issue needed)*

### Summary Table
| Repo | PR | Issue | Status | Skill Synced |
|------|-----|-------|--------|-------------|
| davidsulitzer.com | [#XXX](url) | N/A | Ready for Review | ✅ |
| davidsulitzer.com | [#XXX](url) | [#XXX](url) | Ready for Review | ✅ |
```

> ⚠️ **Do NOT skip sharing links.** Always use full URLs.

---

## What NOT to Do

- **Don't create a skill without researching existing ones** — you might be duplicating
- **Don't write a description that's just the skill name** — the description is routing logic
- **Don't skip "When NOT to Use"** — prevents misfires, improves routing by ~20%
- **Don't leave templates in the system prompt** — put them inside the skill (free when unused)
- **Don't hardcode secrets** — always use `$ENV_VAR` references
- **Don't create the skill in only one repo when it belongs in multiple** — sync all of them
- **Don't skip the quality checklist** — a sloppy skill is worse than no skill
- **Don't forget verification steps in the skill you're writing** — agents make mistakes
- **Don't create skills for one-off tasks** — skills are for recurring workflows

---

## Reference: Skill File Template

```markdown
---
name: <skill-name>
description: <routing-quality description — what, when, when-not>
disable-model-invocation: true
---
# <skill-name>

[Opening line: what this skill does in one sentence]

---

## When to Use

- [Concrete trigger 1]
- [Concrete trigger 2]

## When NOT to Use

- [Anti-trigger 1] → use `/alternative` instead
- [Anti-trigger 2] → just do X directly

---

## Step 1: [First Action]

[Instructions with exact commands]

---

## Step 2: [Second Action]

[Instructions with verification]

---

...

---

## What NOT to Do

- [Guardrail 1] — [why it matters]
- [Guardrail 2] — [why it matters]

---

## Notes

- [Environment info, related skills, edge cases]
```

---

## Reference: Project Field IDs

| Field | Field ID | Key Options |
|-------|----------|-------------|
| **Status** | `PVTSSF_lADOBluP0c4AxnzVzgntIc4` | In Review: `2895eb73`, Done: `782fbd7c` |
| **Priority** | `PVTSSF_lADOBluP0c4AxnzVzg5mgJc` | Low: `9d5cb3c5` |
| **Issue Type: Task** | `IT_kwDOBluP0c4BBYRC` | — |

---

## Reference: Repo Quick Info

| Repo | GitHub | Default Branch |
|------|--------|----------------|
| Monorepo | `stepscode/davidsulitzer.com` | `main` |
| iOS | `8Gaston8/davidsulitzer.com` | `develop` |
| Server | `8Gaston8/davidsulitzer.com` | `develop` |
| Tileserver | `8Gaston8/davidsulitzer.com` | `develop` |

---

## Notes

- **Skill names must be kebab-case** — lowercase, words separated by hyphens
- **One SKILL.md per skill** — each skill lives in its own directory
- **Both `.cursor/` and `.codex/` must always be in sync** within each repo
- **All repos must be in sync** with each other for shared skills
- **Monorepo gets PRs but NO issues** — only the subrepos get issues
- **Test after creating** — always suggest the user tests the skill with a real invocation
- Related skill: `/update-skill` — for updating, renaming, or deleting existing skills
