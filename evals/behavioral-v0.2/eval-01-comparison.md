# EVAL-01 Comparison

## Outcome

Control **38/100**; initial Treatment **77/100**; final Treatment **89/100**. Final delta versus Control: **+51**. Initial-to-final Treatment change: **+12**. UX: Control **4/5**, initial Treatment **5/5**, final Treatment **5/5**.

## Material Unknowns

- Expected: customer/shop/stylist actors; service, duration, stylist choice; slot, hours, holidays, overlap, concurrency and capacity; cancellation, deadline, reschedule, no-show and late arrival; payment/deposit/refund; identity/contact, confirmation, notifications, timezone, walk-ins, and failure/retry.
- Control discovered none of the expected booking territories.
- Initial Treatment discovered customer/shop-operator scope, confirmation, payment/deposit, cancellation timing, rescheduling, and no-show.
- Final Treatment adds service price/duration, stylist choice, account/guest policy, availability source/integration, customer-data lifecycle, reminders, lateness, operator controls, local discovery, and platform.
- Final Treatment still misses exact slot generation, hours/holidays, overlap/concurrency/capacity, refund, timezone, precise walk-in behavior, and failure/retry.
- Treatment-only legitimate discoveries include single-shop versus marketplace topology, operator-tool/data ownership, privacy lifecycle, availability integration, and local discovery. Control-only legitimate discovery is delivery platform, which final Treatment also discovers.

## First Question

Control asks, “먼저 어떤 형태로 만들까요?” Platform affects delivery cost but has lower fan-out than actors and booking ownership. Initial Treatment asks for service scope. Final Treatment makes the customer-only/operator-only/combined alternatives explicit and links salon-side availability and booking-state management to a complete product.

## Ordering

All runs ask one user-facing question. Both Treatments order a product-model decision first. Final Treatment expands its persisted queue to fifteen visible unknowns while keeping the interaction focused; Control starts with channel/platform.

## Evidence First

Control records no repository product-source inspection. Initial Treatment records repository inventory and README inspection. Final Treatment reads the Skill, routed references, schema, template, and validator but records no repository product evidence or inventory; this is a small evidence-first regression. No run asks for a fact that available product evidence already answered.

## Silent Assumptions

No run silently fixes material behavior. Recommendations remain unaccepted, and final Treatment explicitly records that no assumption was accepted as a product decision.

## Premature Build / Closure

No run builds or claims closure. Both Treatments demonstrate `closed: false`; Control gates implementation on clarification and approval.

## State Discipline

Initial Treatment creates validated revision 1 with five material unknowns. Final Treatment creates validated revision 1 with fifteen material unknowns, OPEN status, no approval, and no downstream objects requiring impact links. Control creates no durable state; lacking the Treatment contract is a comparative weakness, not a fabricated critical failure.

## Rationalizations

- Control’s “가장 빠르게 쓸 수 있는 MVP” supports platform focus but not placing it ahead of the booking model.
- Initial Treatment links scope to roles, search, inventory, operations, and data ownership.
- Final Treatment recommends the combined surface because availability and booking state require salon-side management, while leaving the recommendation unaccepted.
- No observable language excuses invention, implementation, or closure.

## Verdict

**PASS.** Final Treatment scores **89/100**, exceeds the 85 target, has no critical failure, and improves **+51** over Control and **+12** over initial Treatment. It preserves **5/5** UX while broadening discovery. Exact inventory mechanics, refunds, timezone, and recovery remain documented gaps.
