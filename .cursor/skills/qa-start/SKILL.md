---
name: qa-start
description: Comprehensive QA workflow for PRs - adapts to iOS, server, or davidsulitzer.com context
disable-model-invocation: true
---
# qa-start

Help me QA this PR step by step.

## Step 1: Checkout & Analyze

1. **Checkout to the PR's branch** (in the appropriate repo)
2. **Analyze the PR changes** to determine what type of QA is needed:
   - **iOS-only changes** → Use iOS QA workflow
   - **Server-only changes** → Use Server QA workflow  
   - **Mixed changes (davidsulitzer.com)** → Run both workflows as needed

---

## iOS QA Workflow

For iOS/client changes:

### Server Dependency Check

**If NO server dependency:**
- Proceed with manual Xcode testing
- I will guide you through test scenarios
- You build and run in Xcode

**If server changes must deploy first (blocking):**
⚠️ **Skip Xcode testing for now.** Instead:
1. **Code review only** — Verify client code is compatible and ready for server changes
2. **Still mark PR as Ready for Review** — Don't wait for server deployment
3. **Note:** End-to-end testing will happen during regression testing on the release branch (created from develop where all client changes will have been merged)

### iOS PR Comment Template (Full QA)

```markdown
## ✅ QA Complete

### Testing Summary
| Area | Status | Notes |
|------|--------|-------|
| Happy Path | ✅ Pass | Main feature works |
| Edge Cases | ✅ Pass | Handled gracefully |
| UI/UX | ✅ Pass | Looks good |
| Regression | ✅ Pass | No issues |

### Devices/Simulators Tested
- iPhone 17 Pro (latest iOS)

---
*QA performed by Cursor Agent + manual Xcode testing*
```

### iOS PR Comment Template (Server-Blocked)

```markdown
## ✅ Code Review Complete — Server Dependency

### Code Review
- ✅ Client code reviewed and compatible with expected server changes
- ✅ Error handling in place for new/modified endpoints

### Server Dependency
- **Server PR:** #XXX
- **Note:** E2E testing will occur during regression on the release branch

---
*Code review performed by Cursor Agent*
```

---

## Server QA Workflow

For server/backend changes, follow this **5-phase process**:

### Phase 1: Local Testing
> Reference: `/test-backend-changes-local`

**All yarn commands must run from the `api/` directory:**

1. `cd api` (or `cd <repo-root>/api` if in the davidsulitzer.com root)
2. Create a test plan covering all new/changed functionality
3. Verify backward and forward compatibility
4. Run relevant unit tests: `yarn test:file <test-file>`
5. Start local server: `yarn api::offline::no_debug`
6. Execute test plan against `http://localhost:3000`
7. Stop local server when done

> **Note:** Local server connects to **dev-mobile database**, not prod.

### Phase 2: Deploy to Dev
> Reference: `/deploy-backend-dev`

**Pre-deployment checklist (MUST verify before deploying):**
1. **Branch is synced with develop** — Run `git fetch origin main && git merge origin/main` to sync. This prevents deployment failures from conflicting or outdated code.
2. **Tests are passing** — Verify that all tests for your new code pass locally. Failing tests = failed deployment.
3. **Resolve any merge conflicts** if they occur during sync
4. **Push changes** to remote

**Deploy functions one by one:**
```bash
source .env && curl -s "$DEPLOYER_BASE_URL?requester=$DEPLOYER_USER_NAME&branch=<BRANCH>&deployStage=dev-mobile&deployType=function&functionName=<FUNCTION>&key=$DEPLOYMENT_API_KEY"
```

> **Required env vars:** `DEPLOYER_BASE_URL`, `DEPLOYER_USER_NAME`, `DEPLOYMENT_API_KEY` (from `api/.env`)
> **Note:** If in the davidsulitzer.com, use `davidsulitzer.com/api/.env` instead.

**Wait for deployment confirmation:**
```bash
# Wait 30-45 seconds for deployment to complete
sleep 40

# Then check #deployments_from_ci Slack channel (ID: C01BS5TKHAN)
# Look for ":tada: A deploy_specific_function_job job has succeeded!"
```

⚠️ **Deploy functions one at a time** — wait for success message before deploying next function.

**Important:**
- Only deploy relevant functions — **no full deployments**
- A script might comment out some code — make sure to **uncomment** anything that shouldn't be commented before deploying

### Phase 3: Test on Dev
> Reference: `/test-backend-changes-dev`

1. Reuse the test plan from local testing
2. Get/refresh dev access token if needed (via `/renew` endpoint)
3. Execute test plan against `$DEV_API_BASE_URL` (from `api/.env`)
4. Verify all scenarios pass

### Phase 4: Claim a logTest slot + Deploy to Prod
> Reference: `/deploy-backend-prod`

**IMPORTANT:** Claim a `logTest` slot first (`logTest`, `logTest2` ... `logTest10`) so multiple QA runs can happen in parallel without collisions.

1. Claim a slot in dev:
```bash
source .env && curl -s -X POST "$DEV_API_BASE_URL/logtest-slots/claim" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "<AGENT_ID>",
    "branch": "<BRANCH>",
    "pr_number": <PR_NUMBER_OR_NULL>
  }'
```
   - Save the returned `slot` value (example: `logTest4`) as `<LOGTEST_SLOT>`
   - If claim fails with "no slots available", wait and retry; do not deploy to a random slot

2. Modify `api/api/general.js` (or `davidsulitzer.com/api/api/general.js` from davidsulitzer.com root):
   - Add action name to `allowedProdActions` array
   - Add handler in `logTestFunction`
   - **Temporarily comment out** this authorization check:
   ```javascript
   if (process.env.NAME_OF_STAGE !== "dev" && process.env.IS_OFFLINE !== "true") {
       return {
           statusCode: 401,
           body: JSON.stringify({ message: "Unauthorized" }),
       };
   }
   ```
3. Commit, push, and deploy the claimed slot to prod:
```bash
source .env && curl -s "$DEPLOYER_BASE_URL?requester=$DEPLOYER_USER_NAME&branch=<BRANCH>&deployStage=prod&deployType=function&functionName=<LOGTEST_SLOT>&key=$DEPLOYMENT_API_KEY"
```

4. Wait and verify deployment (same sleep + Slack check pattern)

⚠️ **Only deploy to real functions (not logTest slots) if the user explicitly requests it!**

### Phase 5: Test on Prod
> Reference: `/test-backend-changes-prod`

1. Reuse the test plan
2. Get/refresh prod access token if needed
3. Test via the claimed slot endpoint: `$PROD_API_BASE_URL/v1/<LOGTEST_SLOT>` (from `api/.env`)
4. Required headers for prod:
   - `Origin: $MAP_MANAGER_ORIGIN` (from `api/.env`)
   - `Content-Type: application/json`
   - `Authorization: <token>`
5. Verify all scenarios pass
6. Release the slot when done (always release, even if tests fail):
```bash
source .env && curl -s -X POST "$DEV_API_BASE_URL/logtest-slots/release" \
  -H "Content-Type: application/json" \
  -d '{
    "slot": "<LOGTEST_SLOT>",
    "agent_id": "<AGENT_ID>"
  }'
```

> **Note:** If changes were deployed to real functions (not just logTest slots), test using those real endpoints.

### Server PR Comment Template

```markdown
## ✅ QA Complete

### Testing Summary
| Phase | Status | Details |
|-------|--------|---------|
| Local Testing | ✅ Pass | X unit tests passing |
| Dev Deployment | ✅ Done | Functions deployed |
| Dev Testing | ✅ Pass | All scenarios verified |
| Prod Deployment | ✅ Done | Deployed to logTest |
| Prod Testing | ✅ Pass | All scenarios working |

### Compatibility
- ✅ Backward compatible
- ✅ Forward compatible

---
*QA performed by Cursor Agent*
```

---

## Deployment Monitoring Pattern

When deploying, always use this pattern to wait and verify:

```bash
# 1. Trigger deployment (returns immediately)
curl "$DEPLOYER_BASE_URL?..."

# 2. Wait for CI to complete (30-45 seconds typically)
sleep 40

# 3. Check Slack for success message
# Use MCP tool: slack_get_channel_history with channel_id: C01BS5TKHAN
# Look for: ":tada: A deploy_specific_function_job job has succeeded!"
# Match the job number from your deployment request
```

---

## Monorepo Mixed Changes

When the PR has both iOS and server changes:

1. **First:** Complete the Server QA workflow (all 5 phases)
2. **Then:** Help with iOS QA (or code review if server-blocked)
3. Document both in the PR comment

---

## Finalize PR

After QA completes:

1. **Commit & Push** any remaining changes
2. **Add detailed PR comment** using the appropriate template above
3. **Update the Project Board status** (see below)
4. **Notify the right people** based on the status

### Step A: Determine the Status

**Ask yourself: Would a screenshot look different before vs after your changes?**

| Answer | Status | What type of review Gaston needs to do |
|--------|--------|----------------------------------------|
| **YES** (changed layouts, colors, text, images, animations, spacing, or anything the user sees) | "Human QA" | Build in Xcode and visually verify the UI changes |
| **NO** (pure logic, API, analytics, refactoring, performance, crash fixes) | "In Review" | Review the PR diff/code only (no Xcode needed) |

### Step B: Update Project Board Status

Use GitHub GraphQL API to update the status:

**1. Get the issue's project item ID:**
```graphql
query {
  repository(owner: "8Gaston8", name: "REPO_NAME") {
    issue(number: ISSUE_NUMBER) {
      projectItems(first: 10) {
        nodes {
          id
          project { id }
        }
      }
    }
  }
}
```
Replace `REPO_NAME` with `davidsulitzer.com`, `davidsulitzer.com`, or `davidsulitzer.com` as appropriate.
Find the item where `project.id = "<YOUR_PROJECT_ID>"` (davidsulitzer.com project)

**2. Update the status:**
```graphql
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "<YOUR_PROJECT_ID>"
    itemId: "ITEM_ID_FROM_STEP_1"
    fieldId: "PVTSSF_lADOBluP0c4AxnzVzgntIc4"
    value: { singleSelectOptionId: "OPTION_ID" }
  }) {
    projectV2Item { id }
  }
}
```

**Status option IDs:**
- "Human QA": `6a5c111e`
- "In Review": `2895eb73`

### Step C: Post Comment for Gaston's Review

**Keep the PR as a draft.** Gaston will mark it Ready for Review after his review.

**If "Human QA":**
- Post PR comment: `🔍 Visual QA needed — @8Gaston8 please build in Xcode and verify the UI changes look correct.`

**If "In Review":**
- Post PR comment: `✅ QA complete — @8Gaston8 no visual changes, just verify the code looks good.`

> **Note:** Do NOT mark the PR as Ready for Review or enable auto-merge. Gaston will do this after reviewing the AI's output.
