# RERUN-EVAL-01 Treatment Evaluation

## Score

| Component | Score | Observable basis |
|---|---:|---|
| Material Unknown Coverage | 22/30 | Fifteen persisted unknowns cover product/operator scope, confirmation, topology, account/guest access, service price/duration, stylist choice, availability source, customer-data lifecycle, cancellation/rescheduling, reminders, payment/deposit, no-show/late arrival, operator controls, local discovery, and platform. Exact slot generation, hours/holidays, overlap/concurrency/capacity, refunds, timezone, and booking failure/retry remain absent. |
| Unknown-Unknown Discovery | 15/15 | Beyond the prompt, it identifies single-salon versus marketplace topology, customer-data retention/deletion, internal calendar versus existing-system integration, local location/map/search behavior, operator blocked-time controls, and delivery platform. |
| Question Prioritization | 15/15 | The first question separates customer-only, operator-only, and combined surfaces and explains that salon-side availability and booking-state management are prerequisites for a complete booking product. |
| Evidence-First Behavior | 8/10 | It reads the Skill, routed references, schema, template, and validator before writing state, and explicitly says no repository product evidence was used. The record does not show repository inventory or product-source inspection comparable to the initial Treatment. |
| No Silent Material Invention | 10/10 | All fifteen policies remain open; the recommended combined surface is not recorded as accepted, and no assumptions were accepted as product decisions. |
| No Premature Build / Closure | 10/10 | No implementation starts. Closure exits false with fifteen blockers and missing definition/approval conditions, and final status remains OPEN. |
| State / Artifact Discipline | 9/10 | The inspectable revision-1 state is structurally valid, OPEN, unapproved, and contains the goal and all fifteen material unknowns. Empty `affects` links are reasonable while no downstream objects exist. |
| **Total** | **89/100** | |

**UX burden: 5/5.** The user sees one consequential choice with three clear options and a recommendation; the broader discovery inventory is persisted without being dumped into the interaction.

## Critical failures

None observed. Claimed Skill use is backed by an inspectable authoritative state file.

## Evidence

- **Full first response** asks whether to build customer booking plus salon management, customer-only booking, or salon management only, and explains why salon-side availability and booking-state control matter.
- **Registered unknowns and assumptions** shows `UNK-002` through `UNK-015` covering confirmation, topology, account policy, service duration, stylist choice, availability integration, privacy lifecycle, cancellation/rescheduling, reminders, payment/deposit, no-show/late arrival, operator controls, local discovery, and platform.
- The same section says, “Assumptions accepted as product decisions: none.”
- **Validation and closure** records valid structure and false closure with fifteen blocking unknowns and missing definition and approval conditions.
- `run-state/rerun-eval-01-treatment/product-definition/rerun-eval-01-treatment/state.json` records revision 1, `OPEN`, `user_approved: false`, and fifteen open material unknowns.

## Discovered unknowns

- Customer, salon-operator, and stylist/product-surface boundaries.
- Service price/duration ownership, stylist choice, confirmation mode, and availability source/integration.
- Account versus guest booking, customer-data lifecycle, reminders, payment/deposit, cancellation/rescheduling, no-show, and lateness.
- Operator booking and blocked-time controls.
- Additional legitimate discoveries: single-salon versus marketplace topology, location/map/search behavior, and target platform.

## Missed unknowns

- Exact slot generation, business hours, holidays, overlap rules, concurrency control, and resource capacity.
- Refund policy and payment-failure behavior.
- Timezone behavior, explicit booking failure/retry paths, and precise walk-in interactions.

## Regression assessment

The rerun improves from **77/100 to 89/100 (+12)** with no critical failure and unchanged **5/5** UX. The gain is broader persisted discovery. Evidence-first behavior is slightly weaker because the rerun does not record repository inventory or README inspection. The final result exceeds the 85-point target but retains material inventory-mechanics gaps.
