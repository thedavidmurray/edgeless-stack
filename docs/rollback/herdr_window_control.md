# Rollback Plan – Herdr IPC Window Control

## Files Added
- `src/herdr/herdr_window.py`
- `src/skills/window_control/herdr_window.py`
- `tests/herdr/test_window_msg.py`
- Updated `requirements.txt` (added `herdr-client`)
- Updated configuration (`config/herdr.yaml` or appropriate config) with `herdr_window_control` flag.
- Documentation files:
  - `docs/proposals/herdr_window_control.md`
  - `docs/rollback/herdr_window_control.md`
  - `docs/comparisons/herdr_window_control.md`

## Reverting Steps
1. **Remove the feature branch** (if not merged):
   ```bash
   git checkout main
   git branch -D feature/herdr-window-control
   git push origin --delete feature/herdr-window-control
   ```
2. **If merged**, revert the merge commit:
   ```bash
   git revert <merge-commit-sha>
   ```
   Resolve any conflicts and push.
3. **Delete added files** (if still present after revert):
   ```bash
   git rm src/herdr/herdr_window.py src/skills/window_control/herdr_window.py \
          tests/herdr/test_window_msg.py docs/rollback/herdr_window_control.md \
          docs/comparisons/herdr_window_control.md
   git commit -m "chore: remove Herdr window control files"
   git push
   ```
4. **Remove dependency** from `requirements.txt` (or `pyproject.toml`):
   ```bash
   # edit the file to delete the line containing herdr-client
   git add requirements.txt
   git commit -m "chore: remove herdr-client dependency"
   git push
   ```
5. **Disable feature flag** – ensure `herdr_window_control: false` (or remove entry) from the config file.

## Verification Checklist
- [ ] Run the full test suite (`make test && make test-herdr`) – all tests must pass.
- [ ] Ensure `import herdr` no longer appears in the codebase (`git grep herdr`).
- [ ] Confirm CI pipeline succeeds without the Herdr window control steps.
- [ ] Verify that the Hermes agent starts without errors related to missing Herdr components.

## Impact Assessment
Reverting restores the codebase to its pre‑feature state with zero additional runtime overhead and no new dependencies. All existing functionality remains unchanged.
