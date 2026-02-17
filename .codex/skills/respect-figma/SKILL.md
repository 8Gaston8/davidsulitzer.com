---
name: respect-figma
description: Fetch design context, screenshots, variables, and assets from Figma and translate them into production code. Works with both the Figma MCP (local/desktop) and the Figma REST API (cloud/CI agents). Trigger when a task involves Figma URLs, node IDs, or design-to-code implementation.
disable-model-invocation: false
---

# Respect Figma

Fetch design data from Figma and translate it faithfully into production code.
Works in **two modes** depending on where the agent is running — see "Choose your tool" below.

For setup details (env vars, config, verification), see `references/figma-config.md`.
For a tool catalog and prompt patterns, see `references/figma-tools-and-prompts.md`.

---

## 0 — Choose Your Tool

| Environment | How to access Figma |
|---|---|
| **Local / desktop** (Cursor, Codex desktop) | Use the **Figma MCP** tools (`get_design_context`, `get_screenshot`, etc.). The MCP server communicates with the running Figma desktop app. |
| **Cloud / CI / headless** (Codex cloud, GitHub Actions) | The MCP is **not available**. Use the **Figma REST API** with an access token from environment secrets. |

### Figma REST API quick reference

Base URL: `https://api.figma.com`

| What you need | Endpoint | Notes |
|---|---|---|
| Design data (node tree, styles, layout) | `GET /v1/files/:fileKey/nodes?ids=:nodeId` | Equivalent to `get_design_context` |
| Rendered image / screenshot | `GET /v1/images/:fileKey?ids=:nodeId&format=png&scale=2` | Equivalent to `get_screenshot` |
| Export SVG asset | `GET /v1/images/:fileKey?ids=:nodeId&format=svg` | For downloading vector assets |
| Variables and styles | `GET /v1/files/:fileKey/variables/local` | Equivalent to `get_variable_defs` |
| File styles | `GET /v1/files/:fileKey/styles` | Color, text, effect, and grid styles |

**Authentication:** `X-Figma-Token: <PERSONAL_ACCESS_TOKEN>` header, or `Authorization: Bearer <OAUTH_TOKEN>`.
Use whatever token is available in your environment secrets (`FIGMA_ACCESS_TOKEN`, `FIGMA_OAUTH_TOKEN`, etc.).

### Extracting fileKey and nodeId from a Figma URL

```
https://figma.com/design/:fileKey/:fileName?node-id=:int1-:int2
```

- `fileKey` → the segment after `/design/`
- `nodeId` → replace the `-` in `int1-int2` with `:` → `int1:int2`

Example: `https://figma.com/design/AbC123/MyFile?node-id=42-99`
→ fileKey = `AbC123`, nodeId = `42:99`

---

## 1 — Required Flow (Do Not Skip)

Whether you are using the MCP or the REST API, the flow is the same conceptually:

1. **Get design context** for the exact node(s).
   - MCP: `get_design_context(nodeId, fileKey)`
   - REST: `GET /v1/files/:fileKey/nodes?ids=:nodeId`

2. **If the response is too large or truncated**, get the high-level node map first, then re-fetch only the required child node(s).
   - MCP: `get_metadata(nodeId, fileKey)` → then `get_design_context` on smaller nodes
   - REST: same endpoint with individual child node IDs

3. **Get a screenshot** for visual reference of the node/variant being implemented.
   - MCP: `get_screenshot(nodeId, fileKey)`
   - REST: `GET /v1/images/:fileKey?ids=:nodeId&format=png&scale=2`

4. **Only after you have both** the design context AND the screenshot, download any needed assets and start implementation.

5. **Translate** the Figma output into the project's conventions, styles, and framework. Reuse existing color tokens, components, and typography.

6. **Validate** the final UI against the Figma screenshot for 1:1 visual parity before marking complete.

> **Always start from the Figma source of truth.** Do not guess icons from code comments, asset names, or SF Symbol approximations.

---

## 2 — Implementation Rules

- Treat the Figma MCP output (typically React + Tailwind) as a **representation of design and behavior**, not as final code style.
- Replace Tailwind utility classes with the project's preferred utilities / design-system tokens when applicable.
- **Reuse existing components** (buttons, inputs, typography, icon wrappers) instead of duplicating functionality.
- Use the project's **color system, typography scale, and spacing tokens** consistently.
- Respect existing **routing, state management, and data-fetch patterns** already adopted in the repo.
- Strive for **1:1 visual parity** with the Figma design. When conflicts arise, prefer design-system tokens and adjust spacing or sizes minimally to match visuals.
- Validate the final UI against the Figma screenshot for both look and behavior.

---

## 3 — Asset Handling

### General rules

- The Figma MCP provides an assets endpoint which can serve image and SVG assets.
- **If the MCP returns a localhost source** for an image or SVG, use that source directly. Do NOT create placeholders.
- **Do NOT import/add new icon packages** — all assets should come from the Figma payload.
- When using the REST API, export assets via `GET /v1/images/:fileKey?ids=:nodeId&format=svg` (or `png`/`pdf`).

### iOS-specific asset workflow

When extracting icons or images for an iOS / Xcode project:

1. Call `get_design_context` (or REST equivalent) on the parent view or the specific node.
2. Identify the asset by its `data-name` attribute and corresponding download URL.
3. Download the SVG from the asset URL.
4. Convert to PDF for the Xcode asset catalog:
   ```bash
   rsvg-convert -f pdf -o icon.pdf icon.svg
   ```
5. Add the PDF to the appropriate `.imageset` directory with a `Contents.json`:
   ```json
   {
     "images": [{ "filename": "icon.pdf", "idiom": "universal" }],
     "info": { "author": "xcode", "version": 1 },
     "properties": { "preserves-vector-representation": true }
   }
   ```
6. Register in SwiftGen's `Assets.swift` (or the project's asset registry).

> **Never substitute SF Symbols or existing assets by name alone.** Always visually verify against the Figma design using `get_screenshot` or the REST images endpoint.

---

## 4 — Link-Based Prompting

- The MCP server is link-based: copy the Figma frame/layer URL and give it to the agent.
- The agent extracts the node ID from the link — it does **not** browse the page.
- Always ensure the link points to the **exact node or variant** you want implemented.
- When given a broad URL (e.g., a full screen), `get_design_context` returns the complete subtree including every nested icon, image, and component with downloadable URLs. Drill into specific `data-node-id` values for individual assets.

---

## 5 — Do NOT

- Do **not** skip `get_design_context` and jump straight to coding from a screenshot alone.
- Do **not** rely on `get_metadata` for finding assets — it only returns the top-level frame without children.
- Do **not** guess colors, spacing, or font sizes. Extract them from the design context or variables.
- Do **not** import new icon libraries (FontAwesome, SF Symbols, etc.) when the Figma payload already provides the asset.
- Do **not** create placeholder images when a real asset URL is available.
- Do **not** hardcode pixel values when the project has spacing/sizing tokens that match.

---

## References

- `references/figma-config.md` — MCP setup, REST API auth, environment variables, verification, troubleshooting.
- `references/figma-tools-and-prompts.md` — Full tool catalog and prompt patterns for selecting frameworks/components and fetching metadata.
