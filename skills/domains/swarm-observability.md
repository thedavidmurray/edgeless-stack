---
name: swarm-observability
description: >
  Instrument multi-agent AI systems with OpenTelemetry and Jaeger. Covers
  auto-instrumentation of framework tool dispatch, trace propagation across
  async handoffs (Discord, queues), pipeline-stage tracing for ingestion
  systems, Tufte-style terminal dashboards from trace APIs, and anomaly
  detection on span telemetry. Designed for Hermes agent swarms but principles
  are framework-agnostic. tags: [observability, otel, jaeger, tracing,
  telemetry, agents, swarm, middleware] triggers: - "instrument agent calls with
  OTel" - "add tracing to agent swarm" - "deploy Jaeger for agent observability"
  - "trace propagation between agents" - "anomaly detection on agent telemetry"
  - "dashboard from Jaeger traces" - "non-invasive framework instrumentation" -
  "dashboard theme system" - "multi-skin aesthetic packs" - "CSS custom
  properties themes" - "retro CRT dashboard variants" - "Electron app with
  themes" category: devops
metadata:
  tags: [opentelemetry, jaeger, observability, tracing, swarm]
  tier: task-specific
  domain: tooling
when_to_apply: When instrumenting a multi-agent system with OpenTelemetry and Jaeger.
---

# Swarm Observability with OpenTelemetry

## One-line summary
Wrap every agent tool call, pipeline stage, and cross-agent handoff in OTel spans, export to Jaeger, and surface a unified trace graph that drills down to vault files, models, providers, and environments.

## When to use this skill
- You need visibility into what an agent swarm actually did (not just what it reported).
- You want post-mortem replay of agent sessions with per-tool duration and error flags.
- You need pipeline health dashboards (throughput, latency, error rates) for ingestion jobs.
- You want anomaly detection driven by span telemetry (phantom stalls, ghost agents, auth cascades, loops).
- You need to instrument a framework (Hermes, LangChain, etc.) without modifying its core files.

## Prerequisites
- Docker (for Jaeger all-in-one)
- `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-exporter-otlp`, `opentelemetry-semantic-conventions` (see `references/dependency-conflicts.md` for version resolution)
- A running OTLP collector or Jaeger instance
- Python 3.10+

## Core workflow

### 1. Deploy Jaeger (check ports first)
```bash
# CRITICAL: check for existing collectors before binding
lsof -i :4317 || true
lsof -i :16686 || true
docker ps --format "table {{.Names}}\t{{.Ports}}"

# If conflicts exist, remap (example: existing collector owns 4317-4318/16686)
docker run -d --name jaeger-edgeless \
  -p 16687:16686 \
  -p 4319:4317 \
  -p 4320:4318 \
  jaegertracing/all-in-one:1.60
```

### 2. Bootstrap OTel in your project
Use the singleton pattern from `templates/otel_setup.py`. Key decisions:
- OTLP gRPC endpoint (e.g., `http://localhost:4319` if remapped)
- Batch span processor for production; simple processor only for tests
- Resource attributes: `service.name`, `host.name`, `deployment.environment`
- Console exporter **opt-in only** via `OTEL_CONSOLE_EXPORT=1` (never default; see Pitfalls)

### 3. Instrument non-invasively (do not edit framework core)
Pattern: `.pth` path injection + runtime monkey-patch.

```bash
# 1. Add project to framework venv so `scripts.lib.*` resolves
# File: venv/lib/python3.11/site-packages/edgeless_otel.pth
# Content (one line): ~/claude-projects
```

```python
# 2. In framework startup files (e.g., cli.py, gateway/run.py), add:
import os
if os.getenv("EDGELESS_OTEL_AUTO", "1") == "1":
    import scripts.lib.hermes_otel_activate  # triggers singleton + patch
```

```python
# 3. Patch the UNIVERSAL dispatch layer — not a branch-specific helper
# Hermes example: model_tools.handle_function_call is called by both
# sequential (tool_executor.py) and concurrent (agent_runtime_helpers.py) paths.
# Patching anything else misses 50% of tool calls silently.
```

See `references/hermes-non-invasive-patch.md` for full reproduction.

### 4. Add trace propagation to handoff messages
When agents dispatch work via text (Discord backroom, queues, etc.), inject W3C `traceparent`:
```
[FROM:Hive][TO:Kilo][TYPE:EXECUTE][TRACE:00-<trace_id>-<span_id>-01]
```
Receiving agent extracts it and continues the span. See `templates/trace_propagation.py`.

### 5. Instrument ingestion pipelines with shared stage tracers
Use `trace_pipeline_stage` and `trace_item_pipeline` context managers (see `templates/ingestion_tracing.py`). This keeps per-item spans consistent across YouTube, RSS, and future sources.

### 6. Build dashboards from the trace API
Query Jaeger's `/api/traces` endpoint directly (see `scripts/trace-dashboard.py` and `scripts/ingestion-dashboard.py`). Render in Tufte-style terminal tables: minimal ink, sparklines, tabular-nums.

For HTML dashboards, see `references/dashboard-aesthetic.md` for a retro-futuristic CRT aesthetic (restricted palette, scanline overlays, phosphor glow, grid-based tiles) that matches sci-fi command-center interfaces.

### 7. Run anomaly detection on span history
`templates/anomaly_detector.py` — calibrated thresholds for agent-specific pathologies:
- Phantom stall: span open >30 min with 0 children → critical; >60 min → kill candidate
- Ghost agent: no heartbeat spans for 30 min
- Auth cascade: unknown provider errors >3x in window
- Loop detection: >5 spans/min with zero file/terminal output spans

## Key techniques

### Technique: Dependency conflict resolution
`mistralai` pins `opentelemetry-semantic-conventions==0.60b1`; `opentelemetry-sdk 1.41.1` requires `0.62b1`. Resolution: force-reinstall the full OTel stack to consistent versions. Do not uninstall `mistralai` unless you confirm nothing else needs it.

### Technique: atexit span flush
Batch processors drop spans if the process exits faster than the export interval. Register `trace.get_tracer_provider().force_flush(timeout_millis=3000)` via `atexit` in your activation module.

### Technique: Agent identity injection for macOS launchd gateways
OTel patches read `HERMES_AGENT_NAME`, `HERMES_PROVIDER`, `HERMES_MODEL` from environment variables. On macOS, gateway processes launched by `launchd` (via `~/Library/LaunchAgents/ai.hermes.gateway-*.plist`) do NOT inherit shell env. Add explicit `<key>EnvironmentVariables</key>` entries to each plist, or use the `HERMES_HOME` fallback:

```python
# In hermes_otel_patch.py — fallback when env vars absent:
_hermes_home = os.environ.get("HERMES_HOME", "")
if _hermes_home:
    _profile = os.path.basename(_hermes_home.strip("/"))
    _AGENT_NAME = _profile.capitalize()  # "hive" → "Hive"
```

`HERMES_HOME` is set by all launchd plists, so this auto-detects every agent without manual edits. See `references/hermes-plist-env-injection.md` for bulk restart commands after patch deployment.

### Technique: Tracing non-Python CLI tools (Claude Code pattern)
For tools written in other languages (Node.js, Rust, shell), you can't import Python OTel libraries directly. Instead, wrap the CLI invocation in a Python script that starts a root span, runs the subprocess interactively (preserving TTY), then emits child spans for detected side effects (git diff, file writes, commits).

```python
# scripts/lib/claude_otel_wrapper.py  — pattern:
# 1. start root span with claude.session
# 2. subprocess.Popen([tool_bin] + args, stdin=stdin, stdout=stdout)
# 3. wait for exit
# 4. git snapshot before/after → emit claude.file.change child spans
# 5. flush spans before exit
```

Install as shell alias: `alias claude='python3 claude_otel_wrapper.py'`. The wrapper runs the real `claude` binary and exports spans to the same Jaeger instance under `service.name=claude-code`.

### Technique: Bidirectional trace↔vault linking
When a vault file is written inside a span, inject `trace_id` into the file's YAML frontmatter. Maintain a SQLite index for reverse lookups (`trace_id → vault_path`). This makes the Jaeger UI conceptually "clickable" to the source document.

### Technique: Return-shape consistency in instrumented wrappers
If you wrap a function that previously returned `(Path, bool)` and the caller now expects `(Path, bool, dict)`, every early-exit path must also return the 3-tuple. A mismatch causes `ValueError: not enough values to unpack` deep in the instrumented pipeline.

### Technique: Postgres bypass for degraded REST APIs
When a REST list endpoint times out at scale (>4,000 items), build a read-only Postgres module (`scripts/lib/paperclip_db.py` pattern) for queries. Keep REST for mutations (checkout, comments). Document the split so future maintainers don't retry the broken endpoint.

### Technique: CORS proxy for HTML dashboards
Jaeger's REST API does not send `Access-Control-Allow-Origin` headers. A dashboard served from `127.0.0.1:8765` cannot fetch `localhost:16687` directly. Use a same-origin Python proxy (see `templates/dashboard-server.py`) that forwards `/jaeger/*` to the Jaeger backend. The dashboard JS then uses `const JAEGER = '/jaeger'` instead of the full origin URL.

### Technique: Multi-skin theme system for dashboards
When users ask for "different aesthetic packs" or "themes" for a dashboard, use CSS custom properties with `data-theme` attributes. One HTML file, one shared structure, multiple personalities selectable at runtime.

Architecture:
- All visual differences are CSS variables (`--bg`, `--border-cyan`, `--font-body`, `--glow-intensity`, etc.)
- Zero structural changes between themes — same grid, panels, charts
- `data-theme` attribute on `<html>` switches skins instantly
- `localStorage` persists choice across restarts
- CRT effects (scanlines, vignette) are per-theme via `--crt-scan` and `--crt-vignette` — set to `transparent` to disable (Minimal theme)

Key CSS patterns:
- **Intensity scaling**: `text-shadow` uses `calc(4px * var(--glow-intensity))` so themes with `0.0` get zero glow without rewriting selectors
- **Font per theme**: Cyberpunk uses Impact headers. Amber uses VT323. Minimal uses SF Mono
- **Panel radius**: `0px` for CRT themes, `6px` for Minimal
- **Theme switcher UI**: Fixed-position swatch buttons in top-right; 18x18px color squares with active glow ring

Six complete skins defined in `templates/electron-theme-system.css`:
| Skin | Colors | Font | CRT | Radius |
|------|--------|------|-----|--------|
| **Phosphor** | Green/cyan/red | Courier | Heavy | 0px |
| **Cyberpunk** | Neon pink/purple | Impact/Courier | Strong glow | 4px |
| **Military** | Olive/brown | Courier | Subtle | 0px |
| **Amber** | Pure amber/gold | VT323 | Warm | 0px |
| **Matrix** | Black/green | Courier | Green-tinted | 0px |
| **Minimal** | Monochrome gray | SF Mono | **None** | 6px |

When packaging as an Electron app, ensure `themes.css` is in `package.json` `build.files` and add a route in `main.js` to serve it. See `references/dashboard-theme-system.md` for full architecture docs and `templates/electron-theme-system.css` for the complete ready-to-use stylesheet.

### Technique: Electron app packaging from HTML dashboards
A dashboard in a browser tab is fragile — users lose the URL, CORS breaks, and the proxy server stops. Package the HTML + proxy + icon as a standalone cross-platform app using Electron. See `references/electron-dashboard-distribution.md` for the full walkthrough and `templates/electron-main.js` for the complete, runnable main process code.

Key decisions:
1. **Embedded proxy**: Node.js `http.createServer` inside `main.js` forwards `/jaeger/*` to Jaeger and serves static HTML on the same origin. Eliminates external Python proxy dependency.
2. **Tray + window**: `BrowserWindow` with `titleBarStyle: 'hiddenInset'` for macOS native feel, plus a tray icon with Show/Open Jaeger/Quit menu.
3. **No external server**: The app starts its own proxy on `127.0.0.1:8766` on launch. Users double-click and it works.
4. **Cross-platform builds**: `electron-builder` produces `.dmg` (macOS), `.exe` (Windows), `.AppImage`/`.deb` (Linux) from a single config.
5. **GitHub releases**: `gh release create` uploads artifacts for distribution.

Quick start:
```bash
npm install electron@^33 electron-builder@^25 --save-dev
# Copy templates/electron-main.js, templates/electron-preload.js, and your index.html
npx electron-builder --mac   # or --win, --linux, or --mac --win --linux
```

Install: `cp -R "dist/mac-arm64/*.app" /Applications/`. Auto-start on login via `osascript` login items.

### Technique: Scrollable grid panels for high-density dashboards
When building multi-panel HTML dashboards, each panel must scroll independently. Apply `overflow-y: auto` to `.panel-content`, not to the grid container. Critical CSS: `min-height: 0` on both the grid container and flex children. Without it, overflow expands the grid cell instead of scrolling.

### Technique: CSS-only data visualization (no canvas, no chart library)
For retro-terminal dashboards, all charts are CSS:
- **Donut**: `conic-gradient` with dynamically-computed segments from JS
- **Sparklines**: flex row of thin vertical `div`s with percentage heights
- **Waveform**: animated random-height bars via `setInterval` updating inline styles
- **Heatmap**: cell backgrounds with rgba intensity mapped to latency thresholds
- **Gauges**: horizontal div fills with CSS transition on width change
This eliminates external chart library dependencies and keeps the aesthetic pixel-perfect.

## Pitfalls

1. **Port conflicts are silent killers.** Always `lsof`/`docker ps` before starting Jaeger. Existing `otel-collector` containers often bind 4317-4318 and 16686. Remap rather than kill — you may break another production collector.

2. **Console exporter default causes CLI spam.** Never enable `ConsoleSpanExporter` by default in production CLIs. It dumps JSON spans to stdout, destroying tabular output and triggering false positives in log parsers. Use OTLP only; opt-in to console via env var.

3. **Patching the wrong dispatch layer misses tool calls.** In Hermes, `agent_runtime_helpers.invoke_tool` is only the concurrent branch. `model_tools.handle_function_call` is the universal layer. Verify with `grep -r "handle_function_call\|invoke_tool"` across the framework before choosing a patch target.

4. **Short-lived CLI processes lose spans.** Cron jobs and one-shot commands exit before the batch processor flushes. atexit `force_flush` is mandatory, not optional.

5. **OTel dependency version skew breaks exports.** After any `pip install` that pulls in `opentelemetry-*`, run `pip check` and verify `semantic-conventions` version matches `sdk` version. Mismatches manifest as silent span drops (no error, no export).

6. **Trace context gets lost in async handoffs.** If you only instrument the sender or only the receiver, you get two disconnected traces. Both sides must implement inject/extract. If the transport is plain text (Discord messages, log lines), encode `traceparent` in a structured field like `[TRACE:...]`.

7. **Instrumenting at the model/token layer is too noisy.** Auto-instrument every LLM request and you drown in spans. Instrument tool calls, handoffs, and file writes — the agent-level semantic units.

8. **Return-shape mismatches in instrumented runners.** When adding a third return value (e.g., metadata dict) to a runner function, audit every `return` statement including early-exit branches. Patch the function, not just the success path.

9. **CORS blocks HTML dashboards silently.** The browser shows "OFFLINE" or blank data, not a CORS error in the main UI. Check the browser console for `fetch` failures. If the dashboard is served from a different origin than Jaeger, a proxy is required (see Technique: CORS proxy).

10. **Decorative random waveforms train users to ignore the signal.** If a dashboard visual uses `Math.random()`, users learn it's fake and stop trusting all visuals. Drive waveforms from real telemetry deltas (spans/second between polls). Label accurately: `"Span Throughput (spans/10s poll)"` not `"Live Signal"`. Use CRT flicker on borders for atmosphere, not fake data.

11. **OTLP exporter blocks on connection, hanging batch CLI tools indefinitely.** The `OTLPSpanExporter` with `BatchSpanProcessor` attempts a gRPC connection during span batch flush. When the collector (Jaeger) is not running, the connection attempt blocks — it does not time out, it does not fail fast. Short-lived CLI processes (cron jobs, one-shot triage scripts, batch processors) exit their main logic successfully but then freeze in the OTel `atexit` shutdown flush. The result is **partial success**: the tool's primary output (archive files, computed results) may be written, but secondary outputs (vault notes, derived JSON, ticket candidates) are never produced. The process is killed by timeout (exit 124), not by error. This is a silent failure mode.

**Fix:** For batch CLI tools, either (a) set `OTEL_SDK_DISABLED=true` in the cron wrapper, (b) make OTLP opt-in via an env var (`OTEL_BATCH_MODE=1` → console-only exporter), or (c) instrument with a non-blocking `SimpleSpanProcessor` + `ConsoleSpanExporter` for CLI contexts. Never rely on `BatchSpanProcessor` + `OTLPSpanExporter` for tools that must exit cleanly without a collector present.

**Detection:** If a cron job reports "timed out after Ns" and the log shows `Transient error StatusCode.UNAVAILABLE encountered while exporting traces to localhost:4319` repeating until kill, this pitfall is active. Check for partial output before assuming total failure. See `rss-triage-pipeline/references/otel-blocking-hang-session-2026-05-26.md` for a full recovery procedure.

## Support files

| File | Type | Purpose |
|------|------|---------|
| `references/hermes-plist-env-injection.md` | reference | macOS launchd plist env vars + HERMES_HOME fallback + bulk gateway restart |
| `references/dependency-conflicts.md` | reference | OTel package version skew and force-reinstall recipe |
| `references/hermes-non-invasive-patch.md` | reference | `.pth` injection, dispatch-layer selection, atexit flush |
| `references/discord-trace-propagation.md` | reference | W3C traceparent in backroom handoff messages |
| `references/paperclip-postgres-bypass.md` | reference | REST timeout workaround pattern |
| `references/return-shape-consistency.md` | reference | Pitfall: instrumented wrapper return tuple changes |
| `references/cli-otel-wrapper.md` | reference | Wrapping non-Python CLI tools (Claude Code, etc.) with OTel spans via Python harness |
| `references/dashboard-aesthetic.md` | reference | Retro-futuristic CRT HTML dashboard: palette, CSS effects, layout rules, scrollable panels, CSS-only charts, data-driven waveforms |
| `templates/otel_setup.py` | template | TracerProvider singleton with OTLP + resource attributes |
| `templates/agent_tracing.py` | template | `@trace_agent_call` decorator + `trace_tool_call()` inline helper |
| `templates/ingestion_tracing.py` | template | Shared `trace_pipeline_stage` / `trace_item_pipeline` context managers |
| `templates/hermes-otel-auto-activation.py` | template | One-line import activation for Hermes (`.pth` + atexit flush) |
| `templates/trace_propagation.py` | template | W3C traceparent inject/extract/continue for async handoffs |
| `templates/anomaly_detector.py` | template | Calibrated anomaly thresholds for agent pathologies |
| `templates/dashboard-server.py` | template | CORS proxy server for HTML dashboards polling Jaeger |
| `templates/electron-main.js` | template | Electron main process with embedded proxy + tray + window |
| `templates/electron-preload.js` | template | Secure IPC bridge for renderer→main process |
| `templates/electron-theme-system.css` | template | Complete 6-skin theme stylesheet with CRT effects, glow scaling, switcher UI |
| `references/electron-dashboard-distribution.md` | reference | Full walkthrough: Electron packaging, DMG, GitHub release |
| `references/dashboard-theme-system.md` | reference | Multi-skin CSS architecture: 6 themes, variable inventory, CRT toggle, Electron packaging notes |
| `scripts/trace-dashboard.py` | script | Runnable CLI dashboard querying Jaeger traces |
| `scripts/ingestion-dashboard.py` | script | Runnable CLI dashboard for ingestion pipeline health |