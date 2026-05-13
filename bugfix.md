# Bugfix Plan: Response HTML not rendered in browser UI

## Goal
Fix the issue where response HTML appears in network responses but does not render in the browser UI for sample apps (including `samples/v2_demo.py` and `samples/test_layouts.py`, and other `samples/*.py` files).

## Scope
Investigate the full rendering path end-to-end, including:
- Python component registration and layout construction in `src/mxlit/components/*`
- Serialization and response payload structure
- Frontend DOM mount/update logic and target selection
- Reactive update mapping (IDs/keys/outputs) and layout containers

## Approach
1. Reproduce with sample apps and capture expected vs actual UI behavior.
2. Trace server-side render payload generation from component APIs through layout manager/context.
3. Trace frontend render pipeline from received payload to DOM updates.
4. Verify component/container schema parity (sidebar, columns, tabs, expander, container, widgets).
5. Identify root cause of dropped or non-mounted content.
6. Define minimal fix with regression coverage from `samples/`.
7. Validate in browser UI (not network-only) and record outcomes.

## Execution Notes
- Follow `.zencoder/chats/5e246da0-643e-4ccb-8f57-1024f146e9f2/plan.md` step gating.
- Follow `README.md` for general functionality expectations
- Pause after investigation findings for user confirmation before implementation.
- Do not modify plan checkboxes from subagents; only master agent updates them.
- No code changes until investigation is complete and approved.
