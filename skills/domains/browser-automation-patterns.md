---
name: browser-automation-patterns
description: >
  Reliable browser automation patterns for web UI tasks using Hermes
  browser/input tools. Covers selector strategy, wait/retry loops, navigation
  guards, state verification, screenshot checkpoints, and failure triage for
  flaky flows. version: 1.0.0 author: Beau metadata: tags: [browser, automation,
  ui-testing, reliability, retry, verification] tier: task-specific domain:
  tooling color: blue prerequisites: commands: [] env_vars: []
metadata:
  tags: [browser, automation, web-ui, patterns]
  tier: task-specific
  domain: product
when_to_apply: >
  When automating browser/web-UI tasks with reliable patterns and the right
  tools.
---

# Browser Automation Patterns

## Identity
A reliability-focused automation operator for browser-driven workflows where flaky timing, dynamic DOM changes, and auth/session drift are common.

## When to Use
- Repeated browser workflows (login, form fill, upload, scrape)
- UI regression checks requiring visual proof
- Tasks where one-shot click/type scripts fail intermittently

## When NOT to Use
- Static API-accessible data (use HTTP/curl first)
- Pure file/text transformations (use terminal/file tools)
- Long unattended recurring runs (use cron with scripts)

## Core Mission
Execute browser tasks deterministically with explicit checkpoints and proof of completion.

## Critical Rules
1. Always define success criteria before first interaction.
2. Use explicit waits tied to observable state (URL/title/element text), not blind sleeps.
3. After each critical action, verify resulting state with screenshot or DOM evidence.
4. On failure, capture diagnostics before retrying (screen + current URL + visible error).
5. Never claim completion without final state verification.

## Instructions

### Phase 1: Preflight
1. Identify target URL and required authenticated state.
2. Define 2-3 observable success markers (e.g., URL path, button disabled, toast text).
3. Clear stale assumptions: refresh page state and confirm starting context.

### Phase 2: Action Execution
1. Navigate to target page.
2. Resolve elements with stable selectors (id/data-testid/role before brittle css chains).
3. Perform one logical action at a time.
4. After each action, wait for a deterministic signal:
   - URL change
   - element appears/disappears
   - known text appears

### Phase 3: Retry Strategy
1. If step fails, capture evidence first.
2. Retry up to 3 times with escalating recovery:
   - retry same action
   - soft refresh + re-find selector
   - full page reload + re-enter flow
3. If still failing, stop and report actionable failure context.

### Phase 4: Verification & Handoff
1. Validate all success markers.
2. Capture final screenshot checkpoint.
3. Summarize: actions performed, verifications passed, remaining risks.

## Deliverables
- Step log (action → wait condition → result)
- Failure diagnostics when applicable
- Final verification evidence (state markers + screenshot path)

## Success Metrics
- Flake rate under 5% across repeated runs
- 100% of critical actions have explicit post-action verification
- 100% completion claims backed by observable evidence

## Common Failure Patterns
- Element detached due to re-render → re-query selector before click
- Hidden modal intercepting click → dismiss modal then retry
- Session timeout redirect → re-auth then resume from known route
- Race condition after submit → wait on backend-completion marker, not animation
- **Google/Microsoft SSO blocks headless browser** → "This browser or app may not be secure"
  - **Root cause:** Google's OAuth detects headless/automated browser user agents and rejects them
  - **Fix:** Use the user's live Chrome browser via CDP (`browser_vision` tools with CDP connection), NOT a headless puppet. The user must already be logged into the target service in their real browser.
  - **Cannot fix by:** Changing user agent, disabling web security, or retrying — Google specifically flags headless Chrome/WebKit.
  - **Alternative:** Have the user generate the asset directly in their logged-in session, then pass the file path to the agent.

- **Opaque rendering surface — custom React/Vue/Canvas event interception**
  - **Symptoms:** `browser_click`, `browser_type`, `browser_press` all appear to execute successfully (no errors), but the target app shows no reaction. Right-click does not open context menus. Double-click does not enter edit mode. Keyboard shortcuts (Space, A, Delete) are silently swallowed. Programmatic JavaScript `dispatchEvent` on SVG/canvas groups has zero effect. Standard DOM querySelector finds elements, but `.click()` on them is ignored.
  - **Root cause:** The app uses a custom rendering layer (React canvas, WebGL, SVG-based node graph, or a proprietary component framework) that intercepts browser events at a level below standard DOM event bubbling. The visible elements are not real interactive DOM nodes — they are painted shapes that the app interprets through its own hit-testing and event pipeline. CDP/Browser Use tools operate at the standard DOM/Devtools Protocol level, which this layer bypasses.
  - **Fix — switch to user-driven execution with guided screenshots:**
    1. Abandon programmatic interaction with the canvas.
    2. Observe the UI state via `browser_vision` screenshots.
    3. Give the user **precise, numbered click instructions** (e.g., "Click the purple Video node in the top-left quadrant of the canvas").
    4. Wait for them to confirm, then screenshot again to verify.
    5. Continue the sequence iteratively.
  - **Alternative — use the app's built-in AI assistant if available:** Many creative platforms (Flora, Figma, etc.) have a chat panel or AI copilot that accepts natural-language commands to manipulate nodes. Type instructions into that chat instead of trying to click the canvas directly.
  - **Alternative — use API/MCP if exposed:** If the platform exposes an API or MCP server, use that instead of browser automation. This is the most reliable path when available.
  - **Cannot fix by:** Changing click coordinates, adding delays, simulating mousemove sequences, or injecting different event types — the interception is architectural, not timing-related.

- **Google Docs / long-form web content extraction**
  - **Symptoms:** `web_extract` returns truncated or heavily summarized content (~5K chars) from a Google Docs `/mobilebasic` URL or long-form single-page article. Critical detail is lost.
  - **Root cause:** The `web_extract` tool caps pages at ~5K chars and applies LLM summarization for large pages. Google Docs mobilebasic pages often exceed this.
  - **Fix:** Use `browser_navigate` + `browser_console` with `document.body.innerText` instead. For very long texts (>50K chars), paginate with `.slice(start, end)`. See `references/google-doc-extraction-pattern.md` for full recipe and verification steps.
  - **Cannot fix by:** Adding `limit` parameter to `web_extract` (no such parameter exists), or retrying `web_extract` (it will always summarize long pages).

- **CDP response channel closed after multi-step SaaS onboarding**
  - **Symptoms:** Browser automation successfully navigates, fills forms, clicks through onboarding, reaches the target page (e.g., `/batch-mode`), then ALL subsequent `browser_navigate` / `browser_click` / `browser_type` calls fail immediately with `Auto-launch failed: CDP response channel closed`. The browser stack becomes completely unrecoverable within the same session. No retry succeeds.
  - **Root cause:** The CDP/WebKit connection crashes during or after heavy JavaScript execution, complex DOM mutations during onboarding, OAuth redirects, or post-registration state transitions. The agent-side CDP client loses the channel and cannot re-establish it.
  - **Fix — abandon browser and switch to programmatic paths:**
    1. **REST API** — if the service exposes one, use curl-based calls (no browser needed)
    2. **User-driven completion** — have the user finish the signup in their live browser, then pass API keys / file paths to the agent
    3. **Pre-register once, automate forever** — for recurring tasks, do the browser registration manually, store tokens in `.env`, and use programmatic auth thereafter
  - **Cannot fix by:** Retrying `browser_navigate`, refreshing the page, restarting the gateway, or adding delays. The CDP connection is permanently broken for that session.
  - **Prevention:** Before attempting browser-based registration for a new SaaS, check if the service offers: (a) a free REST API with key-based auth, or (b) a bulk/batch mode that works without per-item browser interaction. Prefer those over browser automation for multi-step onboarding flows.

## Changelog
- v1.0.0: Initial skill scaffold with deterministic wait/retry/verify workflow.
