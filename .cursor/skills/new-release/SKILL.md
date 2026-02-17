---
name: new-release
description: Prepare a new iOS release — branch, PR, regression testing, App Store submission
disable-model-invocation: true
---
# new-release

Prepare and ship a new iOS release — from creating the branch all the way through to creating the draft GitHub release. For post-Apple-approval steps (publishing, Mixpanel, stability score, issue tracking), see `/release-shipped`.

---

## Step 1: Create the Release Branch

Create a new release branch on the iOS repo from `main`:

```bash
cd <repo-root>
git fetch origin main
git checkout -b release/VERSION origin/main
```

**Branch naming:** `release/VERSION` (e.g., `release/4.31.0`)

> If this is a **hotfix**, work on the existing relevant branch instead of creating a new one from develop.

---

## Step 2: Create the Draft PR

1. Check the diff since the most recent release tag
2. Create a **draft PR** targeting `main` with full details of what changed
3. Assign **Aviad** (`aviadsteps`) as the reviewer
4. Assign **Gaston** (`8Gaston8`) as the assignee
5. Add the label `testflight` to the draft PR

---

## Hotfix PR Management

When creating a hotfix release that cherry-picks commits from existing PRs:

1. **Create the release PR** (e.g., `release/4.28.1` → `develop`) with the cherry-picked commits
2. **Close the original PR(s)** without merging, adding a comment explaining:
   - The changes were cherry-picked into the hotfix release branch
   - Reference the release PR number (e.g., "Closing in favor of Hotfix PR #XXXX")
   - Explain that merging both would create duplicate commits in history
   - Note that the original work is preserved in the closed PR for reference

**Why?** Cherry-picking creates new commits with different SHAs. If both PRs are merged, you get duplicate commits in git history. The release PR should be merged because:
- It has the release tag pointing to its commits
- Keeps git history clean and traceable

---

## Step 3: Create Fibery Release Item

Create a new release item in the Fibery database (nomenclature: `iOS - VERSION`):
https://steps.fibery.io/fibery/space/Product_Pipeline_Space/database/Release

- Link all relevant Fibery dev tasks to the release item
- Share the link with Gaston

---

## Step 4: Update What's New Content

**BEFORE proceeding with regression testing**, update the in-app What's New content:

1. Open `Steps/AppFlows/Whats New/WhatsNewContent.swift`
2. Update the `version` to match the new release version
3. Update `title` with a catchy headline for the main feature
4. Update `features` with 2-4 compelling bullet points
5. Test the What's New sheet appears correctly (Case 22b in regression plan)

**This is a required step for every release with user-facing features!**

If no notable features warrant a What's New announcement, return `nil` from `WhatsNewContent.current`.

---

## Step 5: Regression Testing

Carefully read the regression test plan at `REGRESSION_TESTING_PLAN.md` (in the iOS repo root) and help execute it **one test case at a time**.

### Handling Regression Bugs

When bugs are found during regression testing:

1. **Create a tracking issue** for the release's regression pass (optional but recommended):
   - Title: `[Regression] v{VERSION} Regression Tracking`
   - Description: Summary of bugs found and release risk status
   - Label: `regression`
   - Use `/new-issue` skill with GraphQL for proper project integration

2. **Create focused issues** for each concrete bug:
   - Use `/new-issue` skill and follow its Step 0 pre-research requirements
   - Include reproducible steps, expected vs actual behavior, and impacted files
   - Use relevant domain labels only (for example `regression`, `fastlane`) and avoid generic `bug` label
   - Link related issues in issue body and comments; do not require parent-child/sub-issue hierarchy

3. **Apply triage before fixing** (see `REGRESSION_TESTING_PLAN.md`):
   - Classify each bug by area, risk, and coupling
   - Default fix path: land focused fix PR on `develop`, then cherry-pick/merge into release branch
   - If bugs are unrelated (for example CI/Fastlane + product flow), split into separate PRs
   - Only bundle fixes when they are tightly coupled in one flow/root cause

4. **Execution order**:
   - Continue regression testing and log all issues first
   - Fix blockers/high-risk regressions for the release
   - Track non-blockers into next version when appropriate

---

## Step 6: App Store Release Notes

Once regression testing is over, write a neat, concise, and cool release note for the App Store.

---

## Step 7: Finalize the PR & Project

1. **Update the PR** — convert from draft to ready for review
2. **Update the relevant davidsulitzer.com GitHub project items**, especially:
   - Status
   - iOS Version
   - Server Version
3. **Add a PR comment** summarizing the regression test results clearly

---

## Step 8: Tag & Create Draft GitHub Release

1. **Add a tag** to the latest commit on the release branch: `VERSION` (without any "v" prefix)
2. **Create a draft GitHub release** at https://github.com/8Gaston8/davidsulitzer.com/releases pointing to the tag:
   - Release name: `vVERSION`
   - Include the release notes
   - Add a **"Marketing Story"** section — a very short story to make people *feel* the change that was shipped
   - Add a **"Top Down Metrics Impact"** section describing the expected impact:

**🎯 Q1 2026 North Star:** $1M ARR for davidsulitzer.com

### Top-Down Metrics (Pricing Funnel)
Pricing Screen → Trial Start (goal: 20-25%)
Trial Start → Trial Converted (goal: 35-40%)

### Leading Indicators
🔥 Activation Rate (goal: 60%)
> "% of new trial users who view 5+ place profiles from multi-category searches in their first 7 days"
🔄 Early Retention (goal: 40%)
> "% of trial users with 3+ sessions in first 3 days"
💾 Investment Rate (goal: 10%)
> "% of trial users who save at least 1 place in their first 7 days"

---

## What NOT to Do

- **Don't skip the What's New update** — every release with user-facing features needs it
- **Don't rush regression testing** — log all bugs before starting fixes
- **Don't merge hotfix PRs and the original PRs** — close the original, keep history clean
- **Don't forget to tag the commit** — the tag is needed for the GitHub release
- **Don't publish the GitHub release** — keep it as a draft until the app is approved by Apple (see `/release-shipped`)

---

## Next Step

When Apple approves the release and it's live in the App Store, invoke `/release-shipped` to publish the GitHub release, annotate Mixpanel, and close out project tracking.
