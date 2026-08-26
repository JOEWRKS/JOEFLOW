# Mandatory final-resolution decision reversal

## Initial propagated truth

The Product Agent asked about final-resolution reversibility. The controller answered only: `RMA Agent가 final resolution을 확정하면 되돌릴 수 없다.`

That decision materially propagated as historical `DEC-033` and `RULE-042` across affected requirements, flow, screens, states, data, acceptance criteria, and implementation mapping.

## Injected user change

Only after meaningful propagation, the controller supplied: `생각해보니 최종 처리 저장했다고 무조건 못 바꾸는 건 너무 빡세네. 실제 환불 지급이나 교환 출고가 커밋되기 전까진 RMA 담당자가 사유 남기고 resolution을 다시 열 수 있게 하자.`

## Active replacement

- `DEC-034` supersedes `DEC-033`.
- `RULE-043` supersedes `RULE-042`.
- Reopen applies to the same resolution allocation/partial-quantity scope and requires the currently authorized case owner plus a reason.
- Prior resolution history remains append-only.
- Reopen is permitted only before the relevant downstream execution commit.
- Committed REFUND, REPLACEMENT, RETURN_TO_CUSTOMER, and NO_CREDIT scopes cannot reopen; post-commit error/dispute uses linked correction.
- Cleanup and rollback evidence gates are explicit; committed and unrelated scopes continue independently.

## Verification

- Historical initial decision/rule status: `SUPERSEDED`
- Replacement decision/rule status: active (`ANSWERED` / `CURRENT`)
- Superseded rule present in active truth: no
- Stale affected artifacts after final compilation: `0`
- Closure evaluated only active truth: PASS

