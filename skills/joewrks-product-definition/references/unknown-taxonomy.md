# Unknown Taxonomy

| Class | Meaning | Treatment |
|---|---|---|
| `KNOWN_KNOWN` | Clear fact with evidence | Record source; no question |
| `KNOWN_UNKNOWN` | Recognized missing decision | Ask or resolve from evidence |
| `UNKNOWN_KNOWN` | User has an unstated preference | Use comparison/prototype probe |
| `UNKNOWN_UNKNOWN` | Blind spot absent from initial list | Find via evidence and coverage audit |

Unknown records include `id`, `class`, `question`, `material`, `status`, `source`, `affects[]`, `created_at`, and resolution fields when closed. Material unknowns remain blocking unless `ANSWERED`, `ASSUMED_ACCEPTED`, `DEFERRED_NON_BLOCKING`, or `SUPERSEDED`; a genuinely external blocker remains `BLOCKED_EXTERNAL`.

Do not convert missing evidence into an assumption. `DEFERRED_NON_BLOCKING` requires `source`, `non_blocking_rationale`, and an `impact_assessment` that explicitly records `false` for scope, rules, flows, privacy, money, security, and acceptance. `ASSUMED_ACCEPTED` requires the decision, source, accepting user, and acceptance timestamp.
