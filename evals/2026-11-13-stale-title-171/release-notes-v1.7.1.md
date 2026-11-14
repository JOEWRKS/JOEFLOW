# JOEFLOW 1.7.1

1.7.0 보고서에 "고치지 않은 것"으로 남긴 결함 하나를 고쳤습니다: `projection_check.py`가 손으로 쓴 검토 화면 제목의 낡은 revision을 잡지 못하던 문제. State 0.2.0, 고정 검증 모듈, 바인딩 계약, 기존 승인은 그대로입니다. 상세: [보고서](https://github.com/JOEWRKS/JOEFLOW/blob/main/evals/2026-11-13-stale-title-171/report.md).

## 바뀐 것

- **`projection_check.py`**: 투영 문서의 제목·머리 영역(HTML `<title>`과 첫 섹션 앞 header, Markdown 첫 `## ` 앞)에 적힌 revision(`revision N`, `Revision: N`, `rev N`, `Rev. N`, `개정 N`, `리비전 N` 등)이 state의 `definition_revision`과 다르면 `stale_review_title_revision`(검토 화면)·`stale_spec_title_revision`(기획서) finding(줄·기대값·실제값·다음 행동)을 내고 ok false·종료 코드 1. 기존 키는 그대로이고 `stale_title_revision` 목록만 더했습니다.
- 읽지 않는 것: 본문(변경 이력 등), HTML 주석, JOEFLOW 식별 블록(기존 대조가 맡음), `rev 1→2` 같은 범위(마지막 번호로 봄), "이전/previous/since" 뒤의 과거 rev, `0px`·파일명 속 맨 숫자.
- `update_projection.py`는 바꾸지 않았습니다. 손제목은 자동으로 고치지 않고 finding이 줄 번호와 바꿀 값을 안내합니다.

## 확인된 것

- 1.7.0에서 손제목 `revision 0`이 ok true로 통과하던 것을 재현(`evals/2026-11-13-stale-title-171/repro/`)하고, 후보에서 `<title>`·header 2건이 검출됨.
- 템플릿 형식(`REVIEW VIEW … revision N`, `Planning Review` 제목)은 `update_projection.py` 갱신 뒤 finding 없음.
- 새 테스트 7건. 전체 1,251개 중 실패·오류 8건은 1.7.0 기준(1,244개)과 같은 환경 원인 목록.
- AI-Gomoku rev 44 실제 투영(읽기 전용 사본): 1.7.0·1.7.1 모두 ok true, 과잉 검출 없음.

## 확인되지 않은 것

- 통합 시험 당시의 실제 손제목 문서 원문으로는 시험하지 않았습니다(같은 형태를 다시 만들어 재현).
- `<header>`/`<nav>`/`<section>`/`<h2>`가 없는 자유 형식 HTML에서는 `</h1>`까지만 읽어 머리말 뒷부분의 낡은 rev를 놓칠 수 있습니다.
- "3차 개정", "v2" 같은 표기는 잡지 않습니다.
- 머리 영역에 과거 rev를 "이전" 표시 없이 쓴 제목(예: "rev 43 기능 추가 검토")은 검출됩니다.

## 세션이 대신 내린 결정

1. 기획서(Markdown) H1·머리말도 같은 규칙으로 대조한다.
2. 템플릿 형식의 `REVIEW VIEW` 줄이 낡았는데 식별 블록만 현재인 경우도 검출한다(1.7.0은 통과).
3. 손제목 자동 수정은 하지 않는다.

## 다음 후보 (이번에 고치지 않음)

- JOEDESIGN: 여섯 줄 보고와 결과 목록의 배치 지침 없음, 주입 CSS 측정을 "rendered"와 구별하지 않음.
