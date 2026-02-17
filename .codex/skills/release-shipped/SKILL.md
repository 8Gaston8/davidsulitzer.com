---
name: release-shipped
description: Post-Apple-approval steps — publish release, Mixpanel annotation, close out tracking, assign iOS versions to server & tile-server issues
disable-model-invocation: true
---
# release-shipped

Run this skill **after Apple approves the release and it's live in the App Store**. This handles publishing the GitHub release, annotating Mixpanel, closing out project tracking, and assigning iOS Versions to server/tile-server issues that shipped between releases.

> **Prerequisite:** The `/new-release` skill must have been completed first — the draft GitHub release, tag, and PR should already exist.

---

## Step 1: Publish the GitHub Release

Convert the draft GitHub release to a published (non-draft) release:

```bash
# Find the draft release for this version
gh release list --repo 8Gaston8/davidsulitzer.com --json tagName,isDraft | jq '.[] | select(.isDraft == true)'

# Publish it (replace VERSION with the actual version, e.g. "v4.30.0")
gh release edit VERSION --repo 8Gaston8/davidsulitzer.com --draft=false
```

> **Verify:** `gh release view VERSION --repo 8Gaston8/davidsulitzer.com --json isDraft` should return `false`.

---

## Step 2: Add Mixpanel Annotation

Annotate the release in Mixpanel with the **actual release date** (when Apple made it live, not when it was submitted):

```bash
curl -X POST \
  'https://mixpanel.com/api/app/projects/<YOUR_MIXPANEL_PROJECT_ID>/annotations' \
  --user "$MIXPANEL_SERVICE_ACCOUNT_USERNAME:$MIXPANEL_SERVICE_ACCOUNT_SECRET" \
  -H 'Content-Type: application/json' \
  -d '{
        "description": "iOS VERSION released",
        "datetime": "YYYY-MM-DDTHH:MM:SSZ",
        "tags": ["ios-release", "VERSION"]
      }'
```

> **Note:** `MIXPANEL_SERVICE_ACCOUNT_USERNAME` and `MIXPANEL_SERVICE_ACCOUNT_SECRET` must be set in your environment (from `.env` file at `davidsulitzer.com/api/.env`).

---

## Step 3: List New Mixpanel Events

If any new Mixpanel events were created as part of this release, list them so Gaston can prepare relevant Mixpanel dashboards or reports.

---

## Step 4: Update GitHub Issue Version Tracking — iOS Issues

Check all GitHub issues associated with PRs that have been merged since the last version and update their davidsulitzer.com GitHub project items:

1. **Find merged PRs** since the last release tag
2. **For each merged PR**, find the connected GitHub issues (via GraphQL `timelineItems` with `CONNECTED_EVENT`)
3. **Update the project items** — set the iOS Version field on each issue's project item

```graphql
# Example: Get connected issues for a PR
{
  repository(owner: "8Gaston8", name: "davidsulitzer.com") {
    pullRequest(number: PR_NUMBER) {
      timelineItems(first: 50, itemTypes: [CONNECTED_EVENT]) {
        nodes {
          ... on ConnectedEvent {
            subject { ... on Issue { number title } }
          }
        }
      }
    }
  }
}
```

### Setting the iOS Version field

```graphql
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "<YOUR_PROJECT_ID>"
    itemId: "<ITEM_ID>"
    fieldId: "PVTF_lADOBluP0c4AxnzVzg7CAVA"
    value: { text: "<VERSION>" }
  }) {
    projectV2Item { id }
  }
}
```

> ⚠️ **Always double-check** that the associated PR was merged *after* the previous version was released. Verify by checking the latest commit tags.

---

## Step 5: Assign iOS Versions to Server & Tile-Server Issues

Server and tile-server issues ship independently (via their own deploy cycles), but we want them tagged with the **iOS Version that was current when they shipped**. This creates a unified timeline: when you look at an iOS version, you see everything that shipped around that time.

### The Rule

> If a server or tile-server issue was closed (shipped) between iOS version A's release date and iOS version B's release date, assign it **iOS Version = A**.

### 5a: Build the iOS Release Timeline

```bash
# Get the last N iOS releases with their dates
gh release list --repo 8Gaston8/davidsulitzer.com --limit 20
```

This gives you ordered pairs like:
- `v4.29.0` → `2026-01-27T08:55:57Z`
- `v4.30.0` → `2026-02-12T16:47:11Z`

### 5b: Find Unassigned Server Issues

Query all project items and find those from `davidsulitzer.com` that:
- Have **Status = Done** (shipped)
- Have a **Server Version** set (confirms it's a server issue that was deployed)
- Do **NOT** have an **iOS Version** set

```graphql
# Paginate through all project items (100 at a time)
{
  organization(login: "8Gaston8") {
    projectV2(number: 2) {
      items(first: 100, after: CURSOR) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          fieldValues(first: 20) {
            nodes {
              ... on ProjectV2ItemFieldTextValue {
                text
                field { ... on ProjectV2Field { name } }
              }
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                field { ... on ProjectV2SingleSelectField { name } }
              }
            }
          }
          content {
            ... on Issue {
              number
              title
              repository { name }
              closedAt
              state
            }
          }
        }
      }
    }
  }
}
```

Filter for items where:
- `repository.name == "davidsulitzer.com"`
- `status == "Done"`
- `Server Version` field is set (non-empty)
- `iOS Version` field is empty

### 5c: Find Unassigned Tile-Server Issues

Same query as above, but filter for:
- `repository.name == "davidsulitzer.com"`
- `status == "Done"`
- `Tile Server Version` field is set (non-empty)
- `iOS Version` field is empty

### 5d: Assign iOS Versions

For each unassigned issue, compare its `closedAt` timestamp against the iOS release timeline. Find the **latest iOS release that was released before the issue was closed** — that's the iOS Version to assign.

**Algorithm:**
```
for each unassigned_issue:
    closed_at = issue.closedAt
    ios_version = None
    for release in ios_releases_sorted_by_date_ascending:
        if release.date <= closed_at:
            ios_version = release.version
        else:
            break
    assign ios_version to issue
```

**Set the iOS Version:**

```graphql
mutation {
  updateProjectV2ItemFieldValue(input: {
    projectId: "<YOUR_PROJECT_ID>"
    itemId: "<ITEM_ID>"
    fieldId: "PVTF_lADOBluP0c4AxnzVzg7CAVA"
    value: { text: "<IOS_VERSION>" }
  }) {
    projectV2Item { id }
  }
}
```

### 5e: Verify Assignments

After updating, re-query each item to confirm the iOS Version was set correctly:

```graphql
{
  node(id: "<ITEM_ID>") {
    ... on ProjectV2Item {
      fieldValues(first: 20) {
        nodes {
          ... on ProjectV2ItemFieldTextValue {
            text
            field { ... on ProjectV2Field { name } }
          }
        }
      }
      content {
        ... on Issue { number title }
      }
    }
  }
}
```

### 5f: Report to the User

Present the assignments in a clear table:

| Issue | Repo | Server/Tile Version | Closed | Assigned iOS Version |
|-------|------|---------------------|--------|---------------------|
| #1234 | davidsulitzer.com | 3.140.0 | Jan 20 | 4.28.0 |
| #175 | davidsulitzer.com | 1.38.0 | Feb 5 | 4.29.0 |

Also report any issues that could NOT be assigned (e.g., closed before the earliest known iOS release).

---

## Project Field Reference

| Field | Field ID | Type |
|-------|----------|------|
| **iOS Version** | `PVTF_lADOBluP0c4AxnzVzg7CAVA` | Text |
| **Server Version** | `PVTF_lADOBluP0c4AxnzVzg7CD1Q` | Text |
| **Tile Server Version** | `PVTF_lADOBluP0c4AxnzVzg9t2v4` | Text |
| **Status** | `PVTSSF_lADOBluP0c4AxnzVzgntIc4` | SingleSelect |
| **Project ID** | `<YOUR_PROJECT_ID>` | — |

**Status Option IDs:**
- Done: `782fbd7c`
- Ready for Release: `2f956420`

---

## What NOT to Do

- **Don't run this before Apple approves** — the Mixpanel annotation timestamp must reflect the actual release date
- **Don't forget to publish the GitHub release** — it stays as a draft until this skill is invoked
- **Don't update issue versions for PRs merged before the previous release** — only PRs merged after the last tag
- **Don't skip server/tile-server issues** — they ship independently but still need iOS Version assignment for timeline tracking
- **Don't guess iOS version windows** — always use the actual release dates from `gh release list`, not approximations
- **Don't assign iOS Versions to server/tile-server issues that aren't Done** — only issues with Status = Done and a Server/Tile Server Version set should get an iOS Version

---

## Prerequisites

- `/new-release` must have been completed (draft release, tag, and PR exist)
- The app must be **approved and live** in the App Store
- Environment variables `MIXPANEL_SERVICE_ACCOUNT_USERNAME` and `MIXPANEL_SERVICE_ACCOUNT_SECRET` must be set (from `davidsulitzer.com/api/.env`)
- `gh` CLI must be authenticated with access to `8Gaston8/davidsulitzer.com`, `8Gaston8/davidsulitzer.com`, and `8Gaston8/davidsulitzer.com` repos
