## 결과: rev 2는 승인을 받을 준비가 됐습니다 (ready: true)

- `check_approval.py` 결과: ready: true, errors 없음, revision 2.
- Approval Manifest digest: `6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906`
- Definition digest: `70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182`
- 승인은 기록하지 않았습니다. `record_approval.py --write`는 실행하지 않았고 상태는 그대로 READY_FOR_REVIEW / UNAPPROVED입니다.

## 점검한 것

- **기계 점검:** 상태 검증(`validate_state.py`), 승인 상태(`approval_status.py`), Manifest 생성(`build_approval_manifest.py`), 후보 사전점검(`preflight_state_candidate.py`), 투영 점검(`projection_check.py`)을 돌렸고 모두 통과했습니다. `update_projection.py`는 쓰지 않고 차이만 확인했는데, 두 문서의 식별 블록과 출처표 블록 모두 바꿀 것이 없었습니다.
- **내용 대조:** 기획서와 검토 화면을 state.json과 직접 비교했습니다. rev 2에서 추가된 레코드 7건이 모두 들어 있고 내용도 맞습니다. 조건이 붙은 분기를 무조건으로 바꿔 쓴 곳도 없고, 정본에 없는 내용을 덧붙인 곳도 없습니다. 정본에 정의되지 않은 부분(거부 시 문구, 복구 방법, 제출 뒤 이동)은 "정의되지 않음"이라고 정직하게 적혀 있습니다.

## 바꾼 것

`planning-review-core.html` 하나만 고쳤습니다. 브라우저 탭 제목과 화면 맨 위 제목에 "revision 0"으로 잘못 적혀 있어서 "revision 2"로 바꿨습니다. 다른 곳은 이미 2로 적혀 있었습니다. 기획서와 state.json은 바꾸지 않았습니다.

## 지적했지만 바꾸지 않은 것

- **글자 수 표시 방식이 사용자 확인을 거치지 않았습니다 (가장 중요).** state.json은 "칸 아래 오른쪽에 항상 표시"를 "사용자가 추천안을 수락함"으로 기록해 두었습니다(`DEC-002`, `UNK-002`). 그런데 근거가 된 사용자 원문은 다른 세션이 전달한 "요청 내용 칸에 글자 수 보여줘" 한 문장입니다(`EVD-901`). 이 말은 "요청 폼에 더하고 싶은 것이 있나요?"라는 질문에 대한 답이었고, 사용자는 "항상 표시"와 "180자부터만 표시" 중 하나를 고른 적이 없습니다.
  - 이 기록을 바로잡으려면 rev 3을 열어 정본을 바꿔야 합니다. 그건 투영 문서 결함이 아니라 제품 정의 쪽 문제이고, 승인 준비 범위를 넘습니다.
  - 기획서 §9와 검토 화면의 "승인 전에 확인할 점"에 이 사실과 다른 선택지가 이미 정확히 적혀 있어서, 승인 화면에서 사용자가 직접 확인할 수 있습니다. 그래서 고치지 않았습니다.
  - 사용자가 "180자부터만 표시"를 고르면 rev 2는 승인하지 말고 rev 3으로 다시 열어야 합니다.
- **기획서 섹션 제목 "Approved identity":** 아직 승인 전인데 제목만 보면 승인된 것처럼 읽힙니다. 템플릿에 있는 제목이고, 본문에 "승인 대기"라고 적혀 있어서 그대로 두었습니다.
- **목표 문구 표현 차이:** 같은 목표(`GOAL-001`, 원문 "A requester completes a valid submission")를 기획서 §1은 "끝까지 제출한다", 레코드 표는 "완료한다"로 옮겼습니다. 같은 원문을 다르게 번역한 것이라 고치지 않았습니다.
- **스킬 버전 미기록:** 이 프로젝트가 쓰는 스킬 버전이 기록되어 있지 않다는 안내가 나왔습니다(실행 버전 1.7.0). 기록하려면 `joeflow-project.json`이라는 새 설정 파일을 써야 해서, 지시받지 않은 일이라 하지 않았습니다.

## 남은 것

1. **사용자 승인:** 사용자에게 Manifest와 검토 화면을 보여주고, 특히 "항상 표시"가 맞는지 명시적으로 확인받아야 합니다. 그다음 사용자의 말을 직접 받은 세션이 `record_approval.py ... --revision 2 --manifest-digest 6b50eb33… --quote "..." --write`로 기록합니다.
2. **승인 후 마무리:** `update_projection.py --write`로 두 문서의 승인 표기를 갱신하고 `projection_check.py`를 다시 돌립니다. 그 뒤 인계 문서를 만듭니다.
3. **화면 렌더 확인:** 검토 화면은 `NOT_VERIFIED`로 남았습니다. 브라우저 도구가 로컬 파일 페이지에서는 동작하지 않아 실제 화면을 열어보지 못했습니다.
4. **버전 기록 (선택):** `joeflow_version.py --pin`으로 버전을 기록할 수 있습니다.

## 작업 기록

`<SCRATCH>\r05\commands.log`에 pwd와 명령 12줄을 남겼고 모두 종료 코드 0입니다. 맨 처음 Manifest를 만들려던 명령 하나는 자동 권한 판정에서 거부되어 실행되지 않았으므로 로그에 없습니다. 같은 Manifest 생성은 단순한 형태로 다시 실행했고, 그 줄은 기록되어 있습니다.

수정한 파일: `<SCRATCH>\r05\project\product-definition\request-form\planning-review-core.html`
