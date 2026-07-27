# Herdr IPC Integration – Window Control Proposal

## Motivation & Use‑Cases
- Enable the Hermes agent to control neighboring windows/spaces via the Herdr IPC interface.
- Streamline multi‑window workflows for power users and improve cross‑process coordination.

## Architecture Overview
- **Herdr client** (existing library) → **Hermes agent** (new wrapper) → **Window manager** (macOS CGWindow APIs or X11).
- Communication via JSON‑encoded IPC messages over the Herdr Unix socket.

## New IPC Message Surface
```json
{ "type": "herdr_window", "action": "focus",   "window_id": "<id>" }
{ "type": "herdr_window", "action": "move",    "window_id": "<id>", "space_index": <int> }
{ "type": "herdr_window", "action": "resize",  "window_id": "<id>", "width": <px>, "height": <px> }
```
All messages are gated by the feature flag `herdr_window_control`.

## Affected Components
- `src/herdr/herdr_window.py` – new thin wrapper around the Herdr client.
- `src/skills/window_control/` – will import the wrapper to expose high‑level commands.
- This design document itself (`docs/proposals/herdr_window_control.md`).

## Compatibility & Versioning
- Backwards‑compatible: existing agents ignore unknown `herdr_window` messages.
- Semantic version bump: `x.y.z → x.y.(z+1)` with a `+herdr` pre‑release tag.

## Testing Strategy
- **Unit tests** for message serialization (`tests/herdr/test_window_msg.py`).
- **Integration test** with a mock window manager (`tests/herdr/integration_test.py`).
- CI step `make test-herdr` ensures coverage ≥ 80%.

## Rollback Plan
- See companion rollback document `docs/rollback/herdr_window_control.md` (task t_4e8a3067).

---
*Prepared by builder on $(date)*