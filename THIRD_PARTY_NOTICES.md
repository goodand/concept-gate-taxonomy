# Third-Party Notices

이 저장소가 포함하거나 파생한 서드파티 코드/데이터의 출처와 라이선스 고지.

## TaxoAdapt (Apache-2.0) — `conceptgate/concept_gate_v7.py` 이식분

- 출처: https://github.com/pkargupta/taxoadapt (upstream commit `f7a4212934212e6b132be2c416921958f7c3cd21`)
- 논문: Kargupta et al., "TaxoAdapt", ACL 2025 — https://aclanthology.org/2025.acl-long.1442/
- 라이선스: Apache License 2.0 (사본: `licenses/Apache-2.0-taxoadapt.txt` — 이식분이 남아 있는 한 유지)
- 이식된 부분: `taxonomy.py::Node.get_siblings()`의 부분 이식이
  `concept_gate_v7.py`에 포함됨(파일 내 주석으로 표기, PART B 테스트 대상).
  그 외 프롬프트 구조·분류 접근을 "참고"로 표기한 곳 2건도 같은 파일에 있음.
- read-only 원본 사본(구 `reference/` 4파일 + INTEGRATION_NOTES.md)은
  2026-08-23 제거 — import 0건·통합 완료 후 잔존물이었다. 원문이 필요하면
  git 이력(추가 커밋 `51a1d7b`) 또는 위 upstream commit에서 복원한다.
  **이 고지는 사본이 아니라 이식분에 붙는 것이므로 사본 제거 후에도 유지된다.**

## vendor/obo-relations — OBO Relation Ontology (CC0-1.0)

- 출처: https://github.com/oborel/obo-relations (git subtree)
- 라이선스: CC0-1.0
- 용도: `cg_partwhole.py`가 core.obo의 part_of(BFO:0000050)/has_part(BFO:0000051) 공리를 조립

## vendor/scior — Scior (Apache-2.0)

- 출처: https://github.com/unibz-core/Scior (git subtree)
- 라이선스: Apache-2.0
- 용도: `cg_gufo.py`가 RA02/RA03/RU01 rule metadata(TSV)를 읽기 전용으로 재사용. Scior의 rdflib/owlrl 런타임은 import하지 않음

## gUFO 1.0.0 (CC BY 4.0)

- 출처: https://nemo-ufes.github.io/gufo/ — Almeida, Falbo, Guizzardi, Sales 2019
- IRI: `http://purl.org/nemo/gufo#` / Version IRI: `http://purl.org/nemo/gufo#/1.0.0`
- 라이선스: Creative Commons Attribution 4.0 (CC BY 4.0)
- 용도 1 (어휘 참조): `concept_gate_v7.py`의 UFO stereotype specialization 행렬과 OntoClean 메타게이트의 근거 어휘
- 용도 2 (파일 파생, finding 3): `conceptgate/data/gufo.owl` — 공식 배포 서브셋
  `gufoEndurantsOnly.ttl`(Scior 서브트리 경유)을 RDF/XML로 **무변경 형식 변환**한
  사본. `cg_owl.build_ontology()`가 stereotype 사용 시 `owl:imports`로 선언해
  HermiT가 gUFO disjointness/rigidity 공리를 네이티브 적용. 변환 명령·해시는
  `third_party/sources.lock.json`에 고정
  - 원본 SHA-256: `e5c1557dc2f3fee65ad4b96ca1ea2d036037574d1aba2c620c5ae02d2a24de4d`
  - 변환본 SHA-256: `fc792a35cde0729ae77a94ac4be9d4acb9621cf3f8b46864fe1dee2be6040577`
