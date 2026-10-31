# U2-10 기능 추가 모드 — 오목 rev 39 측정 (2026-10-31)

기존 제품(오목 rev 39, 승인본)에 "기존 동작 유지" 기준선을 넣는 데 드는 작업량. 명령은 `commands.sh`, 생성된 패치는 `patch.json`.

| 단계 | 결과 |
|---|---|
| `new_records.py evidence`(OBSERVED_RUNTIME 1건) + `new_records.py baseline`(동작 4개, `--task`) | 패치: EVD-041, REQ-006, RULE-047, AC-046, SURF-005, TASK-004, Core 행 `coverage[REQ-006]` |
| `open_revision.py --status READY_FOR_REVIEW --write` | rev 41, 검증 오류 0 |
| 손으로 쓴 Core 칸 | 3/20 (goal·happy_path·acceptance; 17칸은 `default_authority` = RULE-047 상속) |
| `build_approval_manifest.py` | 생성(TASK-004가 REQ-006을 매핑) |
| 사본에서 승인 → `validate_closure.py` | `closed: true`, 비영 지표 없음 |

오목이 rev 13~39를 NEW_PRODUCT로 진행하며 기존 앱을 근거로만 쓴 방식을 그대로 두고, 회귀 금지 목록만 보통 권위(REQ+RULE+AC)로 더한다. 새 bootstrap 모드·표면 필드는 만들지 않았다([설계](../../docs/u2-10-u2-11-design.md) 2절).
