# Xarvis Runtime Architecture

Xarvis is a local-first decision runtime with persistent memory.

Current flow:
1. `input.json` is loaded from `examples/demo_full/`
2. guardian validation checks structural and business rules
3. the decision engine chooses an action
4. the result is stored in memory and persisted to SQLite
5. run history can be listed, inspected, exported, or summarized

Primary surfaces:
- `xarvis run demo`
- `xarvis runs list`
- `xarvis runs show <id>`
- `xarvis runs export`
- `xarvis runs stats`
- `xarvis doctor`
