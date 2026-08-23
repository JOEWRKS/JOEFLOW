# Downstream Conformance v0.4.1

This evaluation freezes the first executable downstream conformance layer for approved JOEWRKS Product Definitions. It starts from `main` commit `16fc6edc362321ea03613339e224472b98bc1a04` and does not change canonical Product Definition, interrogation, taxonomy, schema, validators, or Closure semantics.

## Outcome

**HARNESS PASS — frozen implementations correctly reported NONCONFORMANT.**

The Python core executed pinned JavaScript/TypeScript through versioned JSONL adapters and detected:

- Replication A public `confirm_booking` success without booking mutation;
- Replication B B030 rejected-command partial mutation and related second-command bypass;
- Replication B B031 real JavaScript `NaN` and `+Infinity` commit/submission;
- B stale latest-value, historical status projection, overdue clear, and terminal reminder-stop defects.

Positive coverage passed for authority loss, stale no-op, idempotent replay, business-state/delivery separation, and manual delivery retry. The superseded-rule sentinel intentionally produced NONCONFORMANT when `DEC-011` was observed as active.

## Authority pins

- base: `16fc6edc362321ea03613339e224472b98bc1a04`
- v0.4 aggregation: `10e184f2f43dd6f0c5bc6e10bdfeac7223f4464b`
- Replication A: `9408434e640b9cf0bf6afaadd8f9d1f5f52e8943`
- Replication B evidence: `5155a0a348b43804b703b79004bd0bbebff35c0a`
- frozen Replication B source: `eecebc28701006dd2c7be4045a22542e34719705`

## Evidence

- `evidence/frozen-a-evidence.jsonl` — 1 actual public-action record.
- `evidence/frozen-b-evidence.jsonl` — 22 actual engine/selector records.
- `evidence/replication-a-contract.json` — contract SHA-256 `1fb26382fd44d321d0cd3c632af98d73658f5aced1b37141695a203830a9bf16`.
- `evidence/replication-b-contract.json` — contract SHA-256 `c1d10a5330d916fdbe3c15c6039a9ee2f01b4c3f7265f3f1179ab730da8ee768`.
- `evidence/client-feedback-rev44-contract.json` — contract SHA-256 `ea31516b703aab17d471081acf6d49622e0825643c2c4460247396633aecffc2`.
- `evidence/harness-report.json` — Python-core verdicts and component failures.

Responsive behavior is excluded from v0.4.1. No new Figma Make generation or product verdict was performed.
