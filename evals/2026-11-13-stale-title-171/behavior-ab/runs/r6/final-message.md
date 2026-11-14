## 결론
rev 2 승인 준비 결과 **ready: true** 입니다.
- revision: **2**
- Approval Manifest digest: **6b50eb339312a3ad65d6b1645a8769694e07db131843f962189b8d3115bf2906**
- definition digest: 70067b7e163e82909c491a095696086fa648da5caedaf9f035ae72813ca55182

승인은 기록하지 않았습니다(record_approval.py --write 미실행). state.json은 건드리지 않았습니다.

## 점검한 것
- `validate_state.py`: valid.
- `validate_closure.py`: exit 1. 남은 항목은 승인 관련 3개(missing_user_approval, stale_approval, missing_or_stale_approval_manifest)뿐이고, 승인 전이라 정상입니다.
- `build_approval_manifest.py`, `approval_status.py`: rev 2는 UNAPPROVED이고 rev 1만 승인돼 있습니다. rev 1→2 변경은 추가 7건(UNK-002, DEC-002, RULE-002, AC-002, TASK-002, EVD-901, EVD-902)이고 변경·대체·폐기는 0건입니다.
- `projection_check.py`: 처음부터 `ok: true`였지만, 실제 두 문서는 사실상 템플릿 그대로였습니다.
  - 기획서는 `{{CANONICAL_STATE_PATH}}` 자리표시가 남아 있었고, 1~9장이 안내문뿐이었습니다. 레코드 표는 모든 행이 "text"였습니다.
  - 검토 화면은 `<title>`과 `<h1>`이 "revision 0"이었습니다. 이 프로젝트가 1.7.0 스크립트로 돌아서 이 오래된 제목을 잡지 못한 것으로 보입니다. `{{…}}` 자리표시가 7곳 남아 있었고, rev 2에서 더한 글자 수 표시가 어디에도 없었습니다.

## 바꾼 것 (request-form 폴더 안 두 파일만)
- **MASTER_PLANNING_SPEC.md**: 1~9장과 레코드 표를 state.json 내용으로 채웠습니다. 승인 state에 없는 동작은 "정하지 않음"으로 적었고, 새로 지어내지 않았습니다. 정하지 않은 것은 검증 실패 문구, 제출 후 이동, 작은 화면 배치, 접근성입니다. 식별 블록과 출처 표는 그대로 두었습니다.
- **planning-review-core.html**: 제목을 revision 2로 고치고 자리표시를 모두 채웠습니다. 화면 구성도와 FLOW-001 흐름도(유효/무효 분기)를 넣고, rev 2 추가 항목에 NEW 표시를 붙였습니다. Render verification은 `NOT_VERIFIED`로 적었습니다.
- 그다음 `update_projection.py --write`를 돌렸습니다. 식별 블록의 차이는 0이었습니다. `projection_check.py`는 `ok: true`, 남은 자리표시는 0건입니다.

## 남은 것
1. **승인 전에 사용자에게 꼭 확인할 것: UNK-002 / DEC-002의 근거가 약합니다.** 이 질문은 "추천 수락"(BELOW: 칸 아래 오른쪽에 항상 `n / 200`)으로 닫혀 있습니다.
   - 근거로 남은 사용자 말은 다른 세션이 전한 "요청 내용 칸에 글자 수 보여줘" 한 문장(EVD-901)입니다. 이 말은 "요청 폼에 더하고 싶은 것이 있나요?"에 대한 답입니다.
   - 두 안(BELOW / NEAR_LIMIT)을 보고 고른 기록은 없고, `accepted_at`도 비어 있습니다.
   - 사용자가 없어서 state는 바꾸지 않았습니다. 대신 두 문서에 "승인 전에 확인" 항목으로 적었습니다(기획서 9장, 검토 화면의 정책 섹션). 다른 안을 원하면 승인하지 말고 UNK-002를 다시 열어야 합니다.
2. **렌더링은 보지 못했습니다(NOT_VERIFIED).** 브라우저 창에서 file:// 경로를 열지 못했습니다. 로컬 서버를 띄우려면 r6 밖에 launch.json을 써야 해서 하지 않았습니다.
3. **사용자의 실제 승인과 기록이 남았습니다.** 승인을 받으면 그 말을 받은 세션에서 `record_approval.py state.json --revision 2 --manifest-digest 6b50eb33…2906 --at <UTC> --quote "…" --write`를 실행합니다. 이어서 상태·완결성 검증을 다시 돌리고, 두 문서의 승인 상태를 갱신합니다.
4. **이 프로젝트는 JOEFLOW 버전이 고정돼 있지 않습니다.** 지금 1.7.0으로 돌고 있습니다. `joeflow_version.py --pin`으로 한 번 고정해야 하는데, 쓰기 작업이라 하지 않았습니다.

명령 기록 메모: 한 번은 출력을 /tmp로 보내다 실패해서 다섯 명령의 출력을 놓쳤습니다. 거기 적힌 종료 코드는 스크립트 자체의 값이고, 읽기 전용 명령은 다시 실행해 결과를 확인했습니다.

파일은 runs/r6/ 아래: project/product-definition/request-form/MASTER_PLANNING_SPEC.md, project/product-definition/request-form/planning-review-core.html, commands.log
