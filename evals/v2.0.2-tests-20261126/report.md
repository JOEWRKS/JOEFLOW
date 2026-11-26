# JOEFLOW 2.0.2 시험 기록 (2026-11-26)

대상: ATELIER 실사용(23개 리비전) 마찰 JOEFLOW 1~15와 검토 묶음 A·B·C·D·G. 사용자가 2026-11-26에 범위를 확정했습니다(E·F는 2.0.3). 로컬 커밋까지만 했습니다(push·태그·Release·개인 설치 없음). ATELIER는 읽기만 했습니다.

## 1. 묶음별 처리

| 묶음 | 마찰 | 처리 | 확인 |
|---|---|---|---|
| A 기존 질문 닫기 | 6, 7, 8 | `new_records.py resolve UNK --option OPT --words … [--also UNK=OPT]`, `resolve --accept-recommended --pack PACK [--surface SURF]`, `next_product_question.py --grouped [--markdown]`, CLOSE 절 | 재현 rev15(18개 `resolve`, 칸 18개 자동 ADDRESSED), 걷기 시험 33번, `test_builders_202` |
| B 토폴로지 생애주기 | 1, 3, 4, 5, 10 | OPEN 템플릿(UNK-901~906, 근거 없음), 패치 키 `grill_profile`, `question --pack [--axis]`, `topology-on DEC`, `topology-off DEC` | 걷기 시험 1·10~16번, `test_builders_202` |
| C 파생 통일 | 2, 7 | `scripts/decision_policy.py`가 검증기의 `derive_decision_authority`·`classify_materiality`를 부름; 파생이 허용하지 않는 조합은 이유와 함께 거절 | `PolicyTest` 4건, 재현 rev18·22·23의 거절 기록, 메시지 비교 `authority_derivation` |
| D 표면이 비는 순간 | 9 | `requirement --from-decisions … --surface … --requirement …`, `resolve` 보고의 `surfaces_left_without_open_question`, 오류 문구·CLOSE 절 | 재현 rev15(REQ-007·008), 걷기 시험 33~34번, 메시지 비교 `open_surface_without_unknown` |
| G 문구·문서 | 4, 11, 13, 14 | 축별 허용 타입 표(`coverage-inheritance.md`)와 오류 문구, 프로필 칸·`blocks_unknown_refs` 문구, `--draft --full`, 첫 승인 표기, 닫힌 파이프 | [messages/](messages/) 2.0.1·2.0.2 비교 11건 |

기록 문구 수정은 재현에 필요해 `new_records.py edit ID --set|--set-json|--replace-text`를 더했습니다(해결 필드 `status`·`resolution_mode`·`decision_authority` 등은 `edit` 대상이 아님을 드라이버가 지킵니다).

## 2. 재현: ATELIER rev N−1 → 새 빌더 → rev N

드라이버 [replay/replay.py](replay/replay.py)는 커밋된 rev N state에서 작성자가 입력할 말(질문·선택지·사용자 답·결정문·고친 문구)을 읽어 `new_records.py` 명령을 만들고 실행한 뒤 `open_revision.py --write`로 적용합니다. 패치 JSON은 손으로 쓰지 않습니다. 원 패치는 "어느 레코드를 건드렸는가"를 아는 데만 씁니다. 명령과 출력 전부: `replay/<rev>/commands.md`, 결과: `replay/<rev>/result.json`.

```
python -B replay/replay.py --skill <skill> --base <rev N-1 state.json> --target <rev N state.json> --original-patch <ATELIER revN-patch.json> --out <dir> --label revN
```

| 리비전 | ATELIER 커밋 (기준 → 목표) | 명령 | 쓰기 | `definition_digest` | 차이 |
|---|---|---|---|---|---|
| rev15 | `85b2e63` → `8a45625` | resolve 18, requirement 2, edit 4, open_revision 1 | 됨 | **같음** `a3b6d4b0c02a…` | 없음 |
| rev18 | `c26323b` → `ffe8415` | question 1, resolve 1, edit 8, open_revision 1 | 됨 | 다름 (`cab9cf0e…` / 커밋 `fe6aada9…`) | UNK-060·DEC-060 |
| rev22 | `4cc5cd1` → `a3ab5ca` | question 3, resolve 3, edit 12, open_revision 1 | 됨 | 다름 (`40130b2b…` / 커밋 `1f514c6e…`) | UNK·DEC-069·070·071 |
| rev23 | `a3ab5ca` → `03dc151` | question 2, resolve 2, edit 4, open_revision 1 | 됨 | 다름 (`9edb5337…` / 커밋 `0bac274e…`) | UNK·DEC-072·073 |

rev18·22·23은 재진입에서 새로 묻고 같은 리비전에 답한 질문입니다. 다른 필드는 정확히 다음뿐이고, 드라이버가 그 레코드만 커밋본으로 되돌려 다시 계산하면 digest가 셋 모두 커밋본과 같습니다(`digest_equal_after_restoring: true`).

| 필드 | 새 빌더 | ATELIER 커밋본 | 이유 |
|---|---|---|---|
| 질문·결정 `evidence_refs` | `[]` | `["EVD-001"]` | EVD-001은 사용자 의도(`USER_CONFIRMED_INTENT`)라 `evidence_refs`에 두면 파생이 `EVIDENCE_RESOLVABLE`(증거가 답함)이 되고 빌더는 사용자 답 기록을 거절합니다. first-plan-guide 3절대로 `--reason`(추천 근거)으로 옮겼습니다 |
| 위험 질문(UNK-060·069·070·072)의 `resolution_mode`·`decision_authority`·`accepted_recommendation` | `USER_DECISION`·`USER_DECISION_REQUIRED`·`null` | `USER_ACCEPTED_RECOMMENDATION`·`USER_CONFIRMATION`·수락 객체 | money 플래그(UNK-060·069는 COSTLY_TO_REVERSE도)로 OPEN 파생이 `USER_DECISION_REQUIRED`. 묶음 C대로 위험 질문은 추천을 골라도 사용자 결정으로 기록 |
| 위험 아닌 질문(UNK-071·073) | 모드는 커밋본과 같음 | — | `evidence_refs`만 다름 |

ATELIER 기록이 2.0.1에서 통과한 이유: 질문을 OPEN으로 거치지 않고 RESOLVED로 바로 만들었고, 검증기는 RESOLVED 질문을 다시 파생하지 않습니다. 검증기는 바꾸지 않았으므로 ATELIER state는 2.0.2에서도 그대로 유효합니다. rev15(사용자 답이 이미 `USER_DECISION`이던 축 질문)는 파생과 기록이 일치해 완전히 같습니다. rev15의 edit 4건은 REQ-007·008 materiality(빌더는 표면 materiality를 복사)와 SURF-010·011 `unknown_refs`(ATELIER 세션이 답한 질문을 표면에서 뺌; `resolve`는 빼지 않음)입니다.

재현하지 않은 것: rev14(토폴로지 ON 두 개와 26개 수락), rev2·rev4. `topology-on`은 걷기 시험과 단위 시험으로만 확인했습니다.

## 3. 새 프로젝트 걷기 시험

[walkthrough/run_walkthrough.py](walkthrough/run_walkthrough.py) → [walkthrough/walkthrough.md](walkthrough/walkthrough.md)(38단계, 명령과 출력 그대로), 패치 `rev2~4-patch.json`, 최종 `state.json`.

```
python -B evals/v2.0.2-tests-20261126/walkthrough/run_walkthrough.py skills/joewrks-product-definition evals/v2.0.2-tests-20261126/walkthrough
```

1. 2.0.2 템플릿 → `validate_state` 통과(도메인 6개 OPEN). 2. 묶음 질문표(토폴로지 6). 3~9. 근거 EVD-001, 토폴로지 질문 6개 `resolve`(전부 `USER_DECISION`, 위험 질문). 10. `topology-on DEC-001 --new-surface SURF-001`: MONEY_FLOW 표면, GRILL-MONEY-1 행(digest), 축 질문 12개. 11~15. `topology-off` 5개. 16. rev2 OPEN. 18~29. 축 질문 뼈대를 `--replace question`으로 다시 씀. 30. rev3 OPEN. 31. 추천표(12행, `present_as_one_table: true`). 33. `resolve --accept-recommended`: 결정 12개, 칸 12개 ADDRESSED, `surfaces_left_without_open_question: SURF-001`. 34. `requirement --from-decisions DEC-007..018`: REQ-001, SURF-001 IN_SCOPE. 35. 문구 edit. FREEZE 조각(GOAL·USR·RULE·AC·TASK·Core 행)은 손으로 추가(이 기록들의 빌더는 2.0.2 범위 밖). 36. rev4 READY_FOR_REVIEW 쓰기. 37. `validate_state` 통과. 38. Approval Manifest.

걸린 것: 처음 실행에서 토폴로지 결정 DEC-001~006이 `orphan_material_authority`로 READY_FOR_REVIEW를 막았습니다(어느 coverage 칸에도 묶이지 않음). ATELIER는 DEC-002·005를 REQ-003 Core `boundary`에 묶었습니다. 걷기 시험은 같은 방식으로 REQ-001 `boundary`에 묶었고, `topology-on/-off` 보고 `next_steps`가 이를 알립니다.

## 4. 바뀐 문구 before/after

[messages/run_messages.py](messages/run_messages.py)를 2.0.1(커밋 `1333be3`의 사본)과 2.0.2에 같은 입력으로 돌린 결과: [messages/201.json](messages/201.json), [messages/202.json](messages/202.json).

```
python -B evals/v2.0.2-tests-20261126/messages/run_messages.py <skill> <label> <out.json> <ATELIER rev17 READY state.json>
```

| 장면 | 2.0.1 | 2.0.2 |
|---|---|---|
| 답이 다 나온 OPEN 표면 | `material OPEN surface requires an OPEN UNK-* reference` | 같은 문장 — `SURF-001 is OPEN and material but holds no OPEN question (unknown_refs ['UNK-001']). When every question of the surface is answered, the way out is a requirement as its authority and status IN_SCOPE: new_records.py … requirement --from-decisions DEC-001 --surface SURF-001 --requirement REQ-NNN …` |
| Core 칸 타입 오류 | `COVERED requires only verified exact authority bindings` | … — `axis state: allowed [RULE, STATE], actual FLOW (FLOW-001 /paths)` |
| UX 행동 `back`에 STATE | 같음(2.0.1) | … — `axis back: allowed [FLOW, RULE, SCR], actual STATE (STATE-001 /state_name)` |
| OPEN 토폴로지 칸 | `… OPEN needs current OPEN unknown_refs for the domain pack; …`(모양 목록) | `OPEN needs rationale null, has 'not decided yet'; unknown_refs 'UNK-001' is RESOLVED, not OPEN (an answered domain is ACTIVE or N/A: new_records.py topology-on / topology-off) (shapes: …)` |
| 답한 질문이 `blocks_unknown_refs`에 | `blocks_unknown_refs must resolve to the required current record type` | `blocks_unknown_refs may name only other OPEN unknowns; 'UNK-001' is RESOLVED (drop it: …resolve removes…)` |
| 파생과 다른 권한 | `decision_authority must equal deterministic derivation USER_DECISION_REQUIRED` | … `(high risk: reversibility COSTLY_TO_REVERSE; it is 'USER_CONFIRMATION': new_records.py writes the derived value)` |
| 첫 승인 식별 줄 | `(rev None→1: 추가 15 …)` | `(첫 승인, rev 1: 추가 15 …)` / `(first approval, rev 1: …)` |
| `--draft` 머리 | `## Records changed since revision None …` | `## Records of the first approval …` |
| `--draft --full` | 없음(`unexpected keyword argument 'full'`) | FLOW의 entry·preconditions·paths·outcomes 등 모든 필드 |
| 읽는 쪽이 닫은 파이프 | exit 120, `OSError: [Errno 22] Invalid argument` | exit 0, stderr 없음 |

`invalid_authority_binding_type` 등 보호 모듈(`state_validation_v2.py`·`authority_binding_v2.py`, 해시 고정)의 원 문구는 그대로이고, `explain_state_errors.py`(open_revision이 출력하는 층)가 조건을 덧붙입니다. `validate_state.py` 원 출력은 2.0.1과 같습니다.

## 5. 게이트

- 2.0.1 기준(변경 전, `JOEWRKS_M6_PHASE_B_WORKTREE`=로컬 커밋 `d38b0ca` detached clone): 1,267개, 실패 0·오류 0·건너뜀 6(927초).
- 2.0.2(커밋 `c7b2ec2`, 같은 환경): **1,277개, 실패 0·오류 0·건너뜀 6**(608초, 건너뜀은 기준과 같은 6건). 첫 실행에서 오류 1건(`test_f04_checked_in_pass_and_partial_inputs_are_executable`: F04 이력 픽스처가 템플릿을 sha256으로 묶음)이 나와, 픽스처 경로를 보존한 2.0.1 템플릿 사본(같은 바이트)으로 바꾼 뒤 다시 돌린 결과입니다.
- 명령: `JOEWRKS_M6_PHASE_B_WORKTREE=<d38b0ca snapshot> python -B -m unittest discover -s tests`
- 테스트 변경: `test_builders_202.py` 새 10건. `test_first_plan_201`은 2.0.1 템플릿을 `tests/fixtures/state-v0.2.0-template-2.0.1.json`으로 보존해 씀(그 시험의 대상은 discovery baseline). `test_skill_package`: 버전 2.0.2, 새 모듈 `decision_policy`·`state_builders`, 표준 모듈 `atexit` 허용. 보호 해시(`test_downstream_v2_frozen_boundaries`, legacy 0.1.2.1 고정)는 바꾸지 않았습니다.

## 6. 세션이 내린 설계 결정 (사용자 확인 필요)

1. 위험 질문의 추천 수락은 `USER_DECISION`으로 기록하고 `--accepted`는 거절(위 2절의 digest 차이의 원인). 반대로 가면 검증기 OPEN 파생과 빌더가 다시 어긋납니다.
2. ACTIVE 팩의 행 누락은 계속 오류이고 `topology-on`이 행을 같은 패치에 씁니다(검증 의미 변경 없음). 도메인이 OPEN이면 행이 필요 없습니다.
3. 템플릿 OPEN 칸의 `basis_refs`는 `[]`(검증기가 OPEN에는 근거를 요구하지 않음). 거짓 근거 EVD-900은 없앴습니다.
4. `topology-on` 축 질문은 일반 선택지 두 개(OPT-SPECIFY / OPT-NOT-APPLICABLE)·추천 없음의 뼈대이며, 묻기 전에 `--replace question`으로 다시 써야 합니다.
5. 오류 문구는 보호 모듈을 건드리지 않고 설명 층에서 보강했습니다.
6. 레코드 문구 수정용 `edit`는 원래 범위 밖이지만 "새 빌더만으로 재현"에 필요해 더했습니다.

## 7. 남은 것

- 행동 시험(에이전트가 새 CLOSE 절·빌더를 쓰는지) 없음.
- E(에이전트 기본값 묶음)·F(상태–흐름 린트)는 2.0.3. RULE·AC·TASK 빌더가 없어 걷기 시험의 FREEZE 조각은 손으로 씀.
- 토폴로지 결정의 coverage 묶기(boundary)는 안내만 하고 자동으로 하지 않음.
- 게시(태그·Release·개인 설치)는 사용자 결정 뒤.
