"""등록부에서 **생성된** 문서군 상수 — 손으로 고치지 마라.

정본은 `docs/IDENTIFIER_REGISTER.md` §계열 표이고, 이 파일은 그것을
`scripts/gen_identifier_groups.py` 로 생성한 것이다. 값을 바꾸려면 **등록부를**
고치고 생성기를 다시 돌려라 — `test_identifier_groups_sync.py` 가 둘의 바이트
일치를 강제하므로, 여기만 고치면 게이트가 운다.

**왜 생성하나.** `cg_obligations.py` 가 import 시점에 등록부를 파싱했는데,
production 이 사람이 유지하는 마크다운에 의존하는 것이고 `Dockerfile` 이 `docs/`
를 COPY 하지 않아 배포에서는 무력했다. 생성물은 패키지 안에 있으므로 그 둘이
모두 없어진다.
"""

# 불변식 계열(`I`)을 발행하는 문서군. 판정이 `<문서군>:<글자><번호>` 로
# 불변식을 지목할 때 이 집합으로 해소한다.
INVARIANT_GROUPS: "frozenset[str]" = frozenset({
    "directive",
    "ev-eval",
    "ev-eval-code",
    "h1a-scope",
    "mechspec",
})
