# Third-Party Notices

이 저장소가 포함하거나 파생한 서드파티 코드/데이터의 출처와 라이선스 고지.

## reference/ — TaxoAdapt (Apache-2.0)

- 파일: `reference/taxonomy.py`, `reference/expansion.py`, `reference/classification.py`, `reference/prompts.py`
- 출처: https://github.com/pkargupta/taxoadapt (upstream commit `f7a4212934212e6b132be2c416921958f7c3cd21`)
- 논문: Kargupta et al., "TaxoAdapt", ACL 2025 — https://aclanthology.org/2025.acl-long.1442/
- 라이선스: Apache License 2.0 (사본: `licenses/Apache-2.0-taxoadapt.txt`)
- 변경 여부: **무변경** (upstream과 byte-identical, 참고용 read-only)
- 실제 이식된 부분: `taxonomy.py::get_siblings()`의 부분 이식이 `concept_gate_v7.py`에 포함됨 (PART B 테스트 대상)

## vendor/obo-relations — OBO Relation Ontology (CC0-1.0)

- 출처: https://github.com/oborel/obo-relations (git subtree)
- 라이선스: CC0-1.0
- 용도: `cg_partwhole.py`가 core.obo의 part_of(BFO:0000050)/has_part(BFO:0000051) 공리를 조립

## vendor/scior — Scior (Apache-2.0)

- 출처: https://github.com/unibz-core/Scior (git subtree)
- 라이선스: Apache-2.0
- 용도: `cg_gufo.py`가 RA02/RA03/RU01 rule metadata(TSV)를 읽기 전용으로 재사용. Scior의 rdflib/owlrl 런타임은 import하지 않음

## gUFO (참조 어휘)

- 출처: https://nemo-ufes.github.io/gufo/ (CC BY 4.0)
- 용도: `concept_gate_v7.py`의 UFO stereotype specialization 행렬과 OntoClean 메타게이트의 근거 어휘. 파일 복제 없음(어휘 참조만)
