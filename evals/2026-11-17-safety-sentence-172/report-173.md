# JOEFLOW 1.7.3 후보: digest가 함께 적힌 승인 줄 제외 (2026-11-17)

결론: 머리 영역의 꾸밈말 없는 승인 표기가 마지막 승인 revision과 그 승인의 manifest digest를 같은 줄에 함께 적고 있으면 `projection_check.py`가 더는 낡은 제목으로 잡지 않는다. 2026-11-17 안전 문장 시험 고정물의 5행 오탐이 사라졌고 다른 결과는 같다. 2026-11-15 장면 1·2는 1.7.2와 보고 전체가 같다. 행동 효과는 시험하지 않았다. VERSION은 1.7.2 그대로이고 태그·Release·개인 설치는 하지 않았다.

코드 커밋: `b16ddd4` (fix: projection_check skips an approval line carrying the last approval digest). 근거 장면: [behavior-ab/report.md](behavior-ab/report.md), 고정물 [behavior-ab/fixture/](behavior-ab/fixture/).

## 변경

`skills/joewrks-product-definition/scripts/projection_check.py`

- `check()`가 `approval_status(state)["last_approved_revision"]`과 같은 revision의 `approval_history[].manifest_digest`를 읽어(`_approval_digest`, 같은 revision이 여러 번이면 마지막 것, 없거나 8자 미만이면 None) `_title_findings(..., last_approved, last_approved_digest)`로 넘긴다. `approval_history` 항목의 필드 이름은 state 스키마 `approval_commitment`(`revision`, `manifest_digest`, …)와 `record_approval.py`가 쓰는 commitment에서 확인했다. `approval.approved_manifest_digest`는 쓰지 않는다. 새 revision이 열리면 그 값은 사라지거나 현재 승인만 가리키기 때문이다.
- `_title_findings`의 1.7.2 제외 조건(숫자 == 마지막 승인, 그리고 `LAST_APPROVED_BEFORE`/`AFTER` 문장)에 세 번째 길 `_carries_approval_digest`를 더했다.
  - 같은 줄: Markdown은 그 원문 줄이다. HTML은 앞뒤의 가장 가까운 블록 태그(`p li h1-6 div td th dd dt blockquote figcaption caption header section nav ul ol main body tr table`) 사이 텍스트이고 머리 영역 경계를 넘지 않는다. `<code>`, `<span>` 같은 인라인 태그 안은 포함한다. 줄바꿈이 있어도 같은 `<p>` 안이면 같은 줄로 본다.
  - digest: 그 텍스트(HTML은 태그를 지운 뒤)에서 앞뒤가 16진수가 아닌 8~64자 16진수 덩어리가 마지막 승인 digest의 앞부분이면 일치다. 대소문자는 무시한다. 백틱·`<code>`·`…`로 감싸도 된다. 7자 이하는 일치로 보지 않는다.
  - 같은 줄에 현재 revision(`HEAD_REVISION`으로 읽은 숫자 == `definition_revision`)도 적혀 있으면 digest 제외를 적용하지 않는다(아래 "결정").
- 1.7.2 주석을 새 규칙에 맞게 고쳤다(꾸밈말 없는 표기는 여전히 읽되 digest 조건이면 제외). `next_action` 문구는 바꾸지 않았다.

`references/workflow-v0.2.0.md`: 제외 규칙 문단의 "a bare … is still read as a title" 뒤에 digest 조건 한 줄을 붙였다. `CHANGELOG.md`: `## 1.7.3 — 후보 (미게시)` 항목.

### 결정: 같은 줄에 현재 revision도 있는 경우

지적을 유지한다. 예: `> revision 2 초안 · 승인 revision 1 (`dd1e837b…`)`. 두 숫자가 한 줄에 있으면 digest가 어느 쪽에 붙은 것인지, 어느 숫자가 문서 이름인지 검사기가 가릴 수 없다. 1.7.2의 설계 의도는 진짜 낡은 제목을 넘기지 않는 쪽을 먼저 지키는 것이다. 그래서 애매한 줄은 지적하고, 사람이 문장꼴("마지막 승인은 revision 1 …")로 쓰거나 줄을 나누게 둔다. 이 줄을 지적해도 비용은 작다. 2026-11-17 B 팔이 쓴 꼴(`> 마지막 승인은 revision 1 (`dd1e837b…`)이고, 이 문서의 revision 2는 아직 승인되지 않았다.`)은 1.7.2 문장 규칙으로 이미 통과하고 테스트로 묶었다.

### 그 밖의 결정

- digest 종류는 마지막 승인의 **manifest digest**만 받는다. 같은 승인의 definition digest는 받지 않는다. 고정물과 identity 블록("이전 승인: rev 1 `dd1e837b…`")이 쓰는 값이 manifest digest이고, 받는 값을 하나로 두어야 완화 폭이 좁다.
- 승인 기록이 없으면(`approval_history` 비어 있음) digest가 None이고 제외도 없다.

## 테스트

`tests/test_projection_check_v020.py`에 `LastApprovedDigestLineTest` 7건을 더했다(state: rev 1 승인, rev 2 승인 대기).

| 테스트 | 기대 | 결과 |
|---|---|---|
| 양성: 기획서 인용 줄 `> 승인: revision 1 (`<8자>…`)`, 전체 64자, 대문자 12자 | 지적 0 | 통과 |
| 양성: 검토 화면 머리 `<p class="note">승인: revision 1⏎(<code><8자></code>…)</p>` | 지적 0 | 통과 |
| 음성: digest 없음 `> 승인: revision 1` | 3행 (2, 1) | 통과 |
| 음성: 다른 digest(rev 2 definition digest 앞 8자), 7자 접두 | 둘 다 지적 | 통과 |
| 음성: 숫자 다름 `revision 0 (<rev1 digest>)`, 승인 기록 없음 | 둘 다 지적 | 통과 |
| 음성: 낡은 `<title>…revision 1</title>` + digest 줄 | `<title>`만 지적. digest가 다른 요소에 있는 낡은 `<h1>`도 지적 | 통과 |
| 결정: 같은 줄에 현재 revision | 지적. 문장꼴은 통과 | 통과 |

- 판별력 확인: `_approval_digest`를 None으로 바꿔 돌리면 양성 2건(부분 시험 4)과 `<title>` 건이 실패한다. 새 규칙이 없으면 이 테스트들이 통과하지 않는다.
- `tests/test_projection_check_v020.py` 24/24 통과(1.7.1 제목 7건, 1.7.2 `LastApprovedSentenceTest` 5건 그대로).
- `test_skill_package`, `test_v2_installed_workflow`, `test_v2_reentry_workflow_contract`, projection 테스트를 함께 돌리면 73/73 통과(workflow·CHANGELOG 수정 뒤).
- 전체(`python -B -m unittest discover -s tests -p 'test*.py'`): 1.7.3 후보는 1,263개 중 실패 3·오류 5·건너뜀 1. 같은 명령을 같은 작업 트리에서 변경을 stash한 1.7.2 상태로 돌리면 1,256개 중 실패 3·오류 5·건너뜀 1. 실패·오류 8건 목록이 줄 단위로 같다(`diff` 일치). 1.7.2 보고서가 적은 환경 원인 8건이다(discovery baseline digest 2, projection audit F04 fixture 1, reverse bootstrap schema 2, migration 구조 스키마 2, downstream 2.1 dogfood replay 1).

## 고정물 재검사 (`projection_check.py`, 1.7.3 후보 `b16ddd4`)

| 고정물 | 1.7.2 결과 (저장된 json) | 1.7.3 결과 | 나머지 키 |
|---|---|---|---|
| 2026-11-17 안전 문장 (`behavior-ab/fixture/`) | ok false, spec 5행 heading (기대 2, 실제 1) | **ok true, 지적 0** (exit 0) | stale_identity·missing·changed·retired, review 전부 같음 |
| 2026-11-15 장면 1 (낡은 손제목) | ok false, review `<title>` 6행·header 23행 (2, 0) | 같음 (exit 1) | 보고 전체 동일 |
| 2026-11-15 장면 2 (`> 승인 revision 1 기준으로 작성됨 (현재 rev 2 검토 중)`) | ok false, spec 5행 (2, 1) | 같음 (exit 1) | 보고 전체 동일 |

장면 2의 5행은 digest가 없고 현재 revision 2도 같은 줄에 있다. 두 이유 모두로 여전히 지적된다.

## 확인된 것

- digest가 함께 적힌 사실 줄(고정물 5행 형태, 기획서와 검토 화면 머리)은 지적되지 않는다.
- digest 없음, 다른 digest, 7자 이하, 숫자 다름, 승인 기록 없음, 같은 줄에 현재 revision이 있으면 지적된다. 낡은 `<title>`·`<h1>`은 digest 줄이 옆에 있어도 지적된다.
- 1.7.1·1.7.2 테스트와 두 날짜의 고정물 결과는 바뀌지 않았다(11-17 5행만 사라짐).
- `next_action` 문구는 바이트 그대로다.

## 확인되지 않은 것

- **행동 효과는 시험하지 않았다.** 이 변경으로 에이전트가 사실 줄을 다시 쓰지 않게 되는지(11-17 시험에서 8/8이 다시 썼다)는 유료 하위 에이전트 시험이 필요하다. 이번 범위에서는 하지 않았다. 지적이 사라지므로 다시 쓸 동기도 사라질 것으로 보이지만 관찰은 아니다.
- **반대 위험(진짜 낡은 이름을 넘김)의 남은 길:**
  1. 문서가 rev 1 때 "기획서 revision 1 · `dd1e837b`"처럼 이름 줄에 digest를 붙여 두었고, rev 2가 열린 뒤 identity 블록만 갱신된 경우다. 이 줄은 넘어간다. 그러나 같은 문서의 `<title>`·`# ` 제목·다른 머리 줄에 rev 1이 남아 있으면 그 줄은 지적된다. identity 블록이 현재 revision·digest를 말하지 않으면 `stale_identity`도 따로 지적한다. 숫자가 "마지막 승인"과 같고 digest가 실제 그 승인의 것이므로, 그 줄 자체는 거짓이 아니다. 문서 이름으로 오해될 여지만 남는다.
  2. **흉내 내기**: identity 블록에 "이전 승인: rev 1 `dd1e837b…`"가 공개돼 있어서, 에이전트가 낡은 제목 줄에 digest를 덧붙여 지적을 없앨 수 있다. 11-17 시험에서 B 3/4가 "제외 규칙을 통과하는 꼴로 다시 쓰기"를 했다. 이런 흉내가 실제로 생기는지는 시험하지 않았다. 범위를 좁히려고 마지막 승인 번호에만, manifest digest에만, 같은 줄에 현재 revision이 없을 때만 제외한다. 그래도 `<title>` 안에 `revision 1 (dd1e837b)`를 쓰면 넘어간다. `<title>`은 문서 이름 그 자체이므로 이 규칙에서 빼는 안도 있었다. 그러나 과제 범위("같은 줄/같은 요소")를 따라 빼지 않았다. 게시 전에 정할 만하다.
- HTML 블록 경계는 태그 이름 목록으로 정한다. 목록 밖 블록 태그(예: `<article>`, `<aside>`)는 경계로 보지 않아서 "같은 줄"이 넓어질 수 있다. 머리 영역 안에서만 읽으므로 영향은 작다고 보지만 시험하지 않았다.
- 개인 설치본에서는 돌리지 않았다. 설치 스크립트도 실행하지 않았다.

## 버전 올리기 핀 (하지 않음, 1.7.2 릴리스 커밋 `6a74446` 기준)

| 파일 | 행 | 지금 |
|---|---|---|
| `VERSION` | 1 | `1.7.2` |
| `skills/joewrks-product-definition/VERSION` | 1 | `1.7.2` (`project_pin.running_version()` / `joeflow_version.py`가 읽음) |
| `README.md` | 10, 165, 183, 341 | `v1.7.2` / `1.7.2` |
| `PROGRAM_ARCHITECTURE.md` | 13, 37 | `v1.7.2`. 268행 뒤에 `v1.7.3` 이력 한 줄 추가 필요 |
| `tests/test_skill_package.py` | 24, 47 | `"1.7.2"`, `` "Program version: **`v1.7.2`**" `` |
| `CHANGELOG.md` | 5 | `## 1.7.3 — 후보 (미게시)` → 날짜·게시 문장 |
| 릴리스 노트 | 새 파일 | `evals/2026-11-17-safety-sentence-172/release-notes-v1.7.3.md` (1.7.2는 27행) |

## 개인 설치 overlay ([install_1_7_3.py](install_1_7_3.py), 실행 안 함)

BASE = `6a74446`(1.7.2 릴리스 커밋, 영수증 `tip_compared`와 같음). TIP은 인자로 받는다: `python -B evals/2026-11-17-safety-sentence-172/install_1_7_3.py <1.7.3 release commit>`. 기본값은 없다. TIP의 skill `VERSION`이 `1.7.3`이 아니거나 BASE가 TIP의 조상이 아니거나 영수증이 1.7.2 설치가 아니면, 설치본을 건드리기 전에 멈춘다. 영수증은 `evals/joeflow-u1-personal-install/personal-install-overlay-receipt.json`에 그대로 둔다.

`6a74446..HEAD`에서 skill 아래 바뀐 파일과 설치 방식:

| 파일 | 방식 |
|---|---|
| `scripts/projection_check.py` | TIP 사본 복사(설치본이 BASE blob과 같은지 먼저 확인) |
| `VERSION` (skill) | 버전 올린 뒤 TIP 사본 복사 |
| `references/workflow-v0.2.0.md` | composed: `patch -F3`로 hunk 적용. `6a74446` blob에 대한 시험 적용은 모든 hunk 성공(scratch 사본) |
| `SKILL.md` | 바뀌지 않음, 건너뜀 |

install_1_7_2.py와 다른 점: TIP을 인자로 받는다. 백업 폴더 이름은 TIP 앞 7자와 실행 날짜에서 만든다. `tip_tracked`는 작업 트리 `ls-files` 대신 `git ls-tree TIP`이다. `program_version_file`은 TIP의 `VERSION`을 읽는다. 날짜를 넘겨 이어 실행하면 새 백업 이름이 생긴다. 이때는 "install source files drifted" 확인에서 멈춘다(안전 쪽).
