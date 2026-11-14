# JOEFLOW 1.7.1 후보 — 검토 화면 손제목의 낡은 revision 검출

결론: `projection_check.py`가 투영 문서의 제목·머리 영역에 적힌 revision이 state의 `definition_revision`과 다르면 `stale_review_title_revision`(검토 화면)·`stale_spec_title_revision`(기획서)로 알리고 ok false·종료 1을 낸다. 본문(변경 이력 등)은 읽지 않는다. 유료 모델 실행 0회.

## 재현 전/후

재현 재료는 [repro/](repro/). 작업 폴더 밖 임시 폴더에서 만들었다.

1. `templates/examples/closed-minimal.state.json`(rev 1 승인) 사본에 1.7.0 통합 시험의 패치(`evals/2026-11-12-friction-170/repro/trial-rev2-patch.json`)로 `open_revision.py --write` → rev 2, READY_FOR_REVIEW([state-rev2.json](repro/state-rev2.json)).
2. 두 템플릿을 채우고 `update_projection.py --write`로 식별 블록을 rev 2로 갱신. 그다음 검토 화면 제목을 손으로 바꿨다: `<title>요청 폼 · 기획 검토 화면 revision 0</title>`, `<h1>요청 폼 기획 검토 (revision 0)</h1>`([review-stale-title.html](repro/review-stale-title.html)). 기획서 끝에는 변경 이력 `- rev 1: 첫 승인`을 넣었다([spec.md](repro/spec.md)). 만든 절차는 [build_repro.py](repro/build_repro.py)(임시 폴더에서 `state.json` 이름으로 실행한 그대로).
3. 1.7.0: [check-before-170.json](repro/check-before-170.json) — `ok: true`, 종료 0. 식별 블록의 `Revision: <code>2</code>`가 "현재 revision이 어딘가에 있다"를 채워서 제목의 0을 보지 않는다.
4. 1.7.1 후보: [check-after-171.json](repro/check-after-171.json) — `ok: false`, 종료 1. `review.stale_title_revision`에 2건(줄 6 `<title>`, 줄 22 header, 기대 2·실제 0, 다음 행동 "line 6: change revision 0 to 2 by hand; …"). 기획서 끝 변경 이력의 `rev 1`은 잡지 않았다.

## 검출 범위와 제외 범위

머리 영역(여기만 읽는다)
- HTML: `<title>` 안, 그리고 `<body>` 시작부터 처음 나오는 `</header>`·`<nav`·`<section`·`<h2` 앞까지. 그런 표지가 없으면 첫 `</h1>`까지.
- Markdown: 첫 `## ` 제목 앞 줄들(H1과 머리말). `## `가 없으면 첫 `# ` 줄 하나.
- `<!-- JOEFLOW:…:BEGIN/END -->` 블록과 HTML 주석은 지운 뒤 읽는다(블록은 기존 대조가 맡는다).

표기: `revision N`, `Revision: N`, `rev N`, `Rev. N`, `rev <code>N</code>`, `` rev `N` ``, `REVISION #N`, `개정 N`, `개정판 N`, `리비전 N`(대소문자 무시). 템플릿의 `REVIEW VIEW … revision N` 줄도 같은 머리 영역이라 함께 대조된다.

제외
- 범위 `rev 1→2`(`->`, `–`, `~`)는 마지막 번호로 본다.
- 바로 앞이 "이전", "직전", "이전 승인", previous, prior, since, from(+approval/approved)이면 과거 언급으로 보고 넘긴다.
- 단어 일부(`prevision 0`), `approval-manifest-r0.json`, `0px` 같은 맨 숫자는 잡지 않는다.
- 머리 영역 밖(본문 섹션, 변경 이력, 표 안의 "rev 23의 기권을 rev 24에서" 같은 문장)은 읽지 않는다.

`update_projection.py`는 바꾸지 않았다. 손제목은 고쳐 쓰지 않고, finding의 `next_action`이 줄 번호와 바꿀 값을 말한다.

## 테스트 결과

- 새 테스트 `StaleTitleRevisionTest` 7건(`tests/test_projection_check_v020.py`): 템플릿을 `update_projection.refresh`로 갱신하면 통과(REVIEW VIEW 줄의 `revision 0`이 1로 바뀌고 finding 없음), REVIEW VIEW 형식 현재 rev 통과, 손제목 낡은 rev 검출(`<title>`·header 2건, 줄·기대·실제·다음 행동), 표기 6종 검출, 본문 이력·주석·범위·"이전 승인"·맨 숫자 미검출, Markdown H1 검출과 `## ` 아래 이력 미검출, CLI 종료 1.
- 전체(`python -B -m unittest discover -s tests -p 'test*.py'`): 1.7.0(HEAD 84b1bb3 임시 worktree) 1,244개 중 실패 3·오류 5, 후보 1,251개(새 7) 중 실패 3·오류 5. 실패·오류 목록 8건이 기준과 같다(discovery baseline digest 2, projection audit F04 fixture 1, reverse bootstrap schema 2, migration 구조 스키마 2, downstream 2.1 dogfood replay 1 — 모두 1.7.0 보고서의 환경 원인 8건).
- 오목 실제 투영(rev 44, `.claude-worktrees/AI-Gomoku/product-definition/ai-coach/` 세 파일을 임시 폴더에 복사해 읽기만): 1.7.0·1.7.1 모두 `ok: true`, `stale_title_revision` 빈 목록, 나머지 키는 같다. 기획서 머리는 1–4줄, 검토 화면 머리는 21–28줄(`REVIEW VIEW · … · revision 44`)이고, 머리말 아래 변경 이력의 rev 12–43은 읽히지 않았다.

## 확인된 것 / 확인되지 않은 것

확인된 것
- 1.7.0 보고서의 결함(손제목 낡은 revision이 ok true)을 재현했고 후보에서 검출된다.
- 템플릿 형식(`REVIEW VIEW … revision N`, `<title>{{project_name}} · Planning Review</title>`)은 갱신 뒤 finding이 없다.
- 오목 rev 44 실제 투영에서 과잉 검출 없음.

확인되지 않은 것
- 1.7.0 통합 시험의 실제 손제목 원문은 보고서에 "revision 0"으로만 남아 있어, 그 문서 자체로는 시험하지 않았다(재현은 같은 형태를 다시 만든 것).
- 머리 영역을 `<header>`/`<nav>`/`<section>`/`<h2>`로 끊지 않는 자유 형식 HTML(예: 첫 `<h2>`가 없이 `<div>`만 있는 문서)에서는 `</h1>`까지만 읽어 머리말 문단의 낡은 rev를 놓칠 수 있다.
- "3차 개정", "v2" 같은 다른 표기는 잡지 않는다.
- 머리 영역에 일부러 과거 rev를 "이전/previous" 없이 적은 문서(예: 제목 "rev 43 기능 추가 검토")는 검출된다. 오목 문서에는 없었다.

## 사용자 대신 정한 것

- 기획서(Markdown)의 H1·머리말도 같은 규칙으로 대조한다(코드 `stale_spec_title_revision`). 과제는 검토 화면을 말했지만 같은 결함이 기획서 제목에도 생길 수 있어서다.
- 템플릿 형식의 `REVIEW VIEW … revision N`이 낡았는데 식별 블록은 현재인 경우도 이제 검출된다(1.7.0은 통과). 보통은 `update_projection.py`가 고치므로 생기지 않는다. 기존 통과 사례(현재 rev)는 그대로다.
- `update_projection.py`가 손제목을 자동으로 고치게 하지 않았다. 손글을 기계가 다시 쓰는 범위를 넓히지 않고 검출·안내만 한다.
- finding은 기존 키 아래 새 키 `stale_title_revision`(목록)으로 넣었다. 기존 키 이름·형태는 그대로다.
- 버전 표기는 VERSION 1.7.0 그대로, CHANGELOG에 1.7.1(미게시)만 적었다.
