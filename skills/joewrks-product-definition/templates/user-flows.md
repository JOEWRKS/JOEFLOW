# User Flows

> Projection of `state.json`; update state first.

For each `FLOW-###`: actor, entry point, preconditions, trigger, happy path, alternatives, failures, recovery, exit, postcondition, related decisions/rules, screens, and acceptance IDs.

```mermaid
flowchart TD
  SCR001[SCR-001 Entry] -->|valid · AC-001| SCR002[SCR-002 Success]
  SCR001 -->|invalid · RULE-001| STATE001[STATE-001 Validation error]
```

