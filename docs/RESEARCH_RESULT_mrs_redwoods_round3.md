# RESEARCH RESULT (3차) — ERG/MRS · Redwoods item locator · 권리 · scope 의미론

- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
- 수신: 2026-08-24, 운영 세션. 발신: 조사용 agent(openai_web_gpt)
- 요청서: `RESEARCH_REQUEST_mrs_redwoods_round3.md` (R1~R6 + Q29.4 schema)
- **개명 근거**: 도착 파일명은 `redwoods_mrs_round3_research_report.md`였다.
  저장소의 조사 왕복 정본 규약은 `RESEARCH_{REQUEST,RESULT}_<주제>.md`이므로
  이름만 규약에 맞췄다. **본문은 1바이트도 고치지 않았다** — §A가 verbatim이고
  아래 sha256이 도착 파일 전체 바이트에 대한 것이다.
- 도착 파일 sha256 (전체 바이트): `8c73df33ae65739c182e4d3dbb9e083e4cdc6788999318b601d472b5891ad2ea`
- 이 문서의 구성: **§A 회신 verbatim** / **§B 운영 세션 수신 검증** —
  §B는 조사의 주장이 아니라 우리 실측이다. 섞어 읽지 마라.

> **적격성 판정은 이 문서에 없다.** 요청서 §"조사에게 적격성 판정을 청하지
> 않는다"대로 회신은 사실만 보고했고(회신 스스로 "Without making an
> eligibility decision"이라 명시), 적격 판정은 D-29 §12의 승격 선행 조건에
> 대한 별도 기계 실측 사안이다. §B가 그 실측의 1차분이다.

---

# A. 회신 verbatim

<!-- VERBATIM-BEGIN -->
# Round 3 Research Report: ERG/MRS and Redwoods Item Locators, Rights, and Scope Semantics

**Research date:** 2026-08-24  
**Scope:** Only the ERG/MRS + Redwoods path requested in the Round-3 research brief.  
**Status convention:** `CONFIRMED`, `PARTIAL`, or `BLOCKED`. `BLOCKED` means the requested fact could not be verified through the attempted paths; it does **not** mean the fact is false or the resource is absent.

## Executive factual summary

1. **A proportional gold record was located at item level.** In a DeepBank 1.1 Redwoods export, item `20214052` from profile `wsj02a` has the surface sentence **“Most are trim.”**, is marked `(active)`, and its MRS contains `_most_q` with both `RSTR` and `BODY` handles. This is an NP quantifier analysis, not a superlative adjective, `at most N`, or `mostly`.
2. **Three cardinal gold records were located at item level.** DeepBank 1.1 items `21438006`, `21618050`, and `20725062` contain `card` with `CARG` values `"3"`, `"2"`, and `"5"`, respectively. In all three, the cardinal EP is distinct from an `udef_q` EP with `RSTR`/`BODY`.
3. **The item-level export used for the concrete MRS snippets is a third-party GitHub mirror.** Official DELPH-IN sources independently establish that the Ninth Growth uses ERG 1214, contains DeepBank WSJ sections 00–21, and that DeepBank 1.1 semantic graphs were released. Therefore the mirror is used as an item locator/evidence copy, **not** as the authority for release rights.
4. **Redwoods-wide metadata says GPL, but that does not erase source-text rights.** The CLARINO/Språkbanken metadata explicitly labels the Redwoods copy `General Public License (GPL)`. The same metadata describes it as hand-annotated and records annotator choices. However, the R1/R2 items are in the `wsj*` DeepBank component, whose underlying Wall Street Journal text carries Dow Jones/LDC restrictions. The exact license statement for the **full DeepBank 1.1 MRS export** was not recovered; that point remains `BLOCKED`.
5. **MRS is deliberately scope-underspecified.** The MRS RFC states that true scopal ambiguities can remain ambiguous. Redwoods treebanking selects a preferred ERG analysis, but the selected analysis can still contain qeq-based scope underspecification. No evidence was found that every gold record contains one human-selected fully scoped resolution. A scope solver can enumerate resolutions, but that enumeration is not itself a human-gold scope choice.
6. **R6 was not triggered.** R1 did not end `BLOCKED`, so the conditional request to search for an alternative DELPH-IN gold treebank outside Redwoods was not pursued as a substitute source.

---

# R1 — Proportional gold item locator in a Redwoods release

## R1.1 Release identity

### Fact

The official DELPH-IN Redwoods documentation identifies the **Ninth Growth** as the latest public Redwoods release and states that it used **ERG 1214**. It also states that the main addition is **DeepBank annotation of Wall Street Journal sections 00–21**, and that semantic graphs from **DeepBank 1.1** were released in multiple formats.

**Official source:**  
https://delph-in.github.io/docs/garage/RedwoodsTop/

Relevant official wording, kept short:

> “The Ninth Growth used the 1214 version of the ERG.”

### Confidence

**High.**

### BLOCKED?

**No** for release-family identification.

---

## R1.2 Concrete proportional record

### Locator

- **Release family:** Redwoods Ninth Growth / ERG 1214 / DeepBank 1.1
- **Component:** DeepBank, Wall Street Journal
- **Profile:** `wsj02a`
- **Item ID:** `20214052`
- **Export evidence:** `Redwoods export of 'wsj02a'`
- **Analysis state:** `[20214052:0] (active)`
- **Evidence-copy path:**  
  `DeepBank1.1/20214052`
- **Evidence-copy URL:**  
  https://github.com/Ayden666/L98Project/blob/6b07252aa1b0d349eba97ab68c388a65be895c02/DeepBank1.1/20214052

### Surface sentence

> `Most are trim.`

This is a bare/partitive NP use of *most*. The selected derivation contains `DET_PRT-NOCMP_DLR`, and the MRS uses `_most_q`; it is therefore not the superlative adjective pattern that caused the earlier false positives.

### MRS fragment

```text
[ _most_q<0:4>
  ARG0: x6
  RSTR: h5
  BODY: h7 ]
[ generic_entity<0:4> ARG0: x6 ]
HCONS: < h5 QEQ h8 ... >
```

The important item-level facts are:

- `_most_q` is an EP in the actual exported record.
- It binds the nominal variable `x6`.
- It has a restrictor handle `h5`.
- It has a body handle `h7`.
- The restrictor is constrained by `h5 QEQ h8` to the `generic_entity` predication.

### Why this counts as a gold/treebank-selected analysis

The record itself says `(active)`. Official Redwoods documentation describes Redwoods as a collection in which, for each utterance, candidate ERG analyses are recorded together with **an annotator decision about the reading preferred in context**:

Official source:  
https://delph-in.github.io/docs/garage/RedwoodsTop/

The CLARINO/Språkbanken copy says the same and explicitly calls Redwoods **hand-annotated**:

https://www.nb.no/sprakbanken/en/resource-catalogue/oai-clarino-uib-no-eng-redwoods/

The official [incr tsdb()] export documentation further states that a thinning export outputs only selected `(active)` trees.

Source:  
https://delph-in.github.io/docs/tools/ItsdbTreebanking_ItsdbExporting/

Thus the mirror’s `(active)` marker is consistent with the standard Redwoods selected-analysis export convention.

### Important provenance qualification

The full textual MRS above was recovered from a **third-party GitHub mirror**, not from an official DELPH-IN download endpoint. The release identity and gold methodology are independently supported by official DELPH-IN sources, but the mirror itself is **not used as a rights authority**.

### Confidence

- Item text and MRS fragment: **High**
- Membership in the DeepBank 1.1 export family: **High**
- Tie between DeepBank 1.1 and Ninth Growth / ERG 1214: **High**
- Rights inferred from the mirror: **None; not inferred**

### BLOCKED?

**No** for the R1 item locator itself.  
**Yes** for the exact rights statement applying to the full DeepBank 1.1 MRS export; see R3.

---

# R2 — Cardinal gold item locators

All three concrete records below are **simple exact cardinals**. No lower-bound or upper-bound example is claimed here.

## R2.1 Item `21438006`

### Locator

- **Profile:** `wsj14b`
- **Item:** `21438006`
- **Evidence-copy path:** `DeepBank1.1/21438006`
- **URL:**  
  https://github.com/Ayden666/L98Project/blob/6b07252aa1b0d349eba97ab68c388a65be895c02/DeepBank1.1/21438006
- **Record state:** `(active)`

### Surface

> `Three companies began trading over the counter.`

### MRS fragment

```text
[ udef_q<0:5> ARG0: x5 RSTR: h6 BODY: h7 ]
[ card<0:5> ARG1: x5 CARG: "3" ]
[ _company_n_of<6:15> ARG0: x5 ]
```

### Structural fact

The quantifier EP and cardinal EP are **distinct**:

- `udef_q` supplies generalized-quantifier structure: `ARG0`, `RSTR`, `BODY`.
- `card` supplies the numerical constant through `CARG: "3"` and points to the same nominal individual via `ARG1: x5`.
- `h6 QEQ h8` connects the quantifier restrictor to the label shared by the cardinal/noun material.

### Cardinal type

**Exact simple cardinal: 3.**

### Confidence

**High.**

### BLOCKED?

**No** for the item locator and MRS structure.

---

## R2.2 Item `21618050`

### Locator

- **Profile:** `wsj16b`
- **Item:** `21618050`
- **Evidence-copy path:** `DeepBank1.1/21618050`
- **URL:**  
  https://github.com/Ayden666/L98Project/blob/6b07252aa1b0d349eba97ab68c388a65be895c02/DeepBank1.1/21618050
- **Record state:** `(active)`

### Surface

> `Two ironies intrude.`

### MRS fragment

```text
[ udef_q<0:3> ARG0: x5 RSTR: h6 BODY: h7 ]
[ card<0:3> ARG1: x5 CARG: "2" ]
[ _irony_n_1<4:11> ARG0: x5 ]
```

### Structural fact

Again, the `card` EP is separate from the `udef_q` EP. Removing only the numerical EP would not syntactically remove the `RSTR`/`BODY` arguments of `udef_q`.

### Cardinal type

**Exact simple cardinal: 2.**

### Confidence

**High.**

### BLOCKED?

**No** for the item locator and MRS structure.

---

## R2.3 Item `20725062`

### Locator

- **Profile:** `wsj07a`
- **Item:** `20725062`
- **Evidence-copy path:** `DeepBank1.1/20725062`
- **URL:**  
  https://github.com/Ayden666/L98Project/blob/6b07252aa1b0d349eba97ab68c388a65be895c02/DeepBank1.1/20725062
- **Record state:** `(active)`

### Surface

> `“Five were interested.”`

### MRS fragment

```text
[ udef_q<0:5> ARG0: x5 RSTR: h7 BODY: h8 ]
[ card<0:5> ARG1: x5 CARG: "5" ]
[ generic_entity<0:5> ARG0: x5 ]
```

### Structural fact

This is a headless numerical NP. The number is represented by `card(CARG "5")`, while `udef_q` independently supplies `RSTR`/`BODY`.

### Cardinal type

**Exact simple cardinal: 5.**

### Confidence

**High.**

### BLOCKED?

**No** for the item locator and MRS structure.

---

## R2.4 What the three actual records establish

These are corpus-level observations, not merely grammar examples:

| Item | Surface cardinal | Quantifier EP | Cardinal EP | Shared nominal variable |
|---|---:|---|---|---|
| `21438006` | three | `udef_q(... RSTR ... BODY ...)` | `card(... CARG "3")` | `x5` |
| `21618050` | two | `udef_q(... RSTR ... BODY ...)` | `card(... CARG "2")` | `x5` |
| `20725062` | five | `udef_q(... RSTR ... BODY ...)` | `card(... CARG "5")` | `x5` |

This directly confirms, in actual exported DeepBank records, the separation that Round 2 had previously established only at the formalism/example level.

---

# R3 — Rights chain: Redwoods GPL metadata versus component rights

## R3.1 Redwoods metadata GPL statement

### Fact

The CLARINO/Språkbanken record for **“LinGO Redwoods Treebank (copy @ INESS)”** explicitly exposes the following fields:

```text
Licence: General Public License (GPL)
dc:rights: Public
dc:rights: GNU
dc:rights: General Public License (GPL)
```

Source:  
https://www.nb.no/sprakbanken/en/resource-catalogue/oai-clarino-uib-no-eng-redwoods/

This is the exact requested location: **resource metadata / Dublin Core rights fields**.

### Confidence

**Very high.**

### BLOCKED?

**No** for what the metadata says.

### Limitation

The metadata-level GPL statement must not be silently treated as a relicensing of every underlying source text. DELPH-IN’s installation documentation explicitly warns that individual public LOGON components use different licenses and directs users to component directories or file headers for details:

https://delph-in.github.io/docs/tools/LogonInstallation

Accordingly, component text rights are reported separately below.

---

## R3.2 Ninth Growth component groups and source/right status

The official Ninth Growth inventory is here:

https://delph-in.github.io/docs/garage/RedwoodsTop/

| Component/profile group | Source described by DELPH-IN | Rights fact found | Status |
|---|---|---|---|
| `wsj*` / DeepBank | Wall Street Journal, sections 00–21 | Underlying WSJ material has Dow Jones/LDC restrictions; DeepBank annotation rights are a separate layer | **PARTIAL** |
| `ws01`–`ws13`, `ws214` | Wikipedia / WeScience | `ws01/LICENSE` in ERG 1214 states CC BY-SA 3.0 for adapted English-Wikipedia material | **CONFIRMED for inspected WeScience profile** |
| `vm*` | Verbmobil scheduling dialogues | Source identified; no component-specific rights statement recovered in this round | **BLOCKED** |
| `ec*` | E-commerce customer-service email | Source identified; no component-specific rights statement recovered in this round | **BLOCKED** |
| `jh*`, `ps*`, `tg*`, `rondane`, `hike` | LOGON travel brochures | Source identified; no profile-specific rights statement recovered in this round | **BLOCKED** |
| `sc*` and Brown/SemCor-derived profiles | SemCor/Brown-derived data | Source family identified; no single Ninth-Growth component license statement recovered | **BLOCKED** |
| `cb` | Eric Raymond, *The Cathedral and the Bazaar* | Source identified. In the inspected ERG 1214 `tsdb/gold/cb` directory no `LICENSE` file was present | **BLOCKED** |
| `rtc000`, `rtc001` | Tanaka/Pacling corpus | Source identified; no component-specific rights statement recovered | **BLOCKED** |
| WeScience user-generated web profiles | user-generated web content | Source described by official Redwoods page; exact per-profile rights not recovered here | **BLOCKED** |
| small constructed test suites | linguistic test material | not used for R1/R2; rights not expanded in this round | **BLOCKED / not material to located items** |

### Explicit WeScience license evidence

The ERG 1214 profile file:

`tsdb/gold/ws01/LICENSE`

states, in relevant part:

> “licensed under the Creative Commons Attribution-ShareAlike license, version 3.0.”

Locator:  
https://github.com/delph-in/erg/blob/1214/tsdb/gold/ws01/LICENSE

### Confidence

**High** for component identities.  
**High** for the inspected `ws01` license.  
**Low / BLOCKED** where no component statement was recovered.

---

## R3.3 Rights of the R1/R2 component: DeepBank / Wall Street Journal

All four located items (`20214052`, `21438006`, `21618050`, `20725062`) belong to `wsj*` profiles and therefore the **DeepBank Wall Street Journal component**.

### Underlying text rights

Official Redwoods inventory labels `wsj*` as Wall Street Journal text and links to LDC.

Source:  
https://delph-in.github.io/docs/garage/RedwoodsTop/

LDC’s WSJ-containing releases explicitly identify Dow Jones copyright. For example, the ACL/DCI catalog states:

> “Portions © 1987-1989 Dow Jones & Company, Inc.”

Source:  
https://catalog.ldc.upenn.edu/LDC93T1

The associated README also states that the user agrees not to redistribute the material outside the research group.

Source:  
https://catalog.ldc.upenn.edu/docs/LDC93T1/acldci.readme.html

This is sufficient to establish that **the raw WSJ text is not made unrestricted merely by the Redwoods GPL metadata**.

### DeepBank annotation layer

Official DeepBank 1.0 documentation states that its annotations were distributed via META-SHARE under the META-SHARE Commons Attribution Share-Alike license.

Source:  
https://delph-in.github.io/docs/garage/DeepBank_OneZero/

However, this statement is explicitly about **DeepBank 1.0**. It is not promoted here to a DeepBank 1.1 license.

### DeepBank / SDP Version 1.1 distribution

The SemEval-2015 Task 18 data page states that large portions of the data are derivative of PTB/LDC resources and that participants needed to enter an LDC license agreement to obtain training/development/test data. The page later records a **Version 1.1** release through LDC.

Sources:

- https://alt.qcri.org/semeval2015/task18/index.php?id=data-and-tools
- https://alt.qcri.org/semeval2015/task18/

This Version 1.1 distribution is a semantic-dependency task distribution, not proof of the license for the **full MRS Redwoods export** used in R1/R2.

### Result

The following distinctions are factual:

1. **Redwoods metadata:** GPL — confirmed.
2. **WSJ source text:** LDC/Dow Jones restricted/copyrighted — confirmed.
3. **DeepBank 1.0 annotation package:** META-SHARE Commons Attribution Share-Alike — confirmed for 1.0.
4. **SemEval/SDP Version 1.1 derived data:** LDC agreement required — confirmed.
5. **Full DeepBank 1.1 MRS export used by the item mirror:** exact data-specific license statement — **not recovered**.

### Confidence

**High.**

### BLOCKED?

**Yes** for the exact license governing the full DeepBank 1.1 MRS export.

This must remain `BLOCKED`, not “no license”.

---

# R4 — Canonical MRS grammar and adapter-relevant semantics

## R4.1 Canonical MRS definition: EPs, handles, and handle constraints

### Canonical sources

1. **DELPH-IN MRS RFC**  
   https://delph-in.github.io/docs/tools/MrsRFC/

2. **ERG Semantics: Basics**  
   https://delph-in.github.io/docs/erg/ErgSemantics_Basics/

3. **Formalism tutorial**  
   https://delph-in.github.io/docs/howto/DelphinTutorial_Formalisms/

### Formal facts

The MRS RFC defines an EP in terms of:

- a **handle/label**,
- a **predicate**,
- ordinary variable arguments,
- scopal arguments,
- and, in modern MRS, optional constant content such as a numeric/name string.

An MRS contains:

- a distinguished top handle,
- a bag of EPs,
- a bag of handle constraints,
- plus modern index/individual-constraint information.

The ERG uses `qeq` handle constraints for its normal scope underspecification mechanism.

Short RFC wording:

> “true scopal ambiguities can be left ambiguous”

### Adapter-relevant consequence

`RSTR` and `BODY` are **handle-valued scopal arguments**, not ordinary entity variables. Therefore an adapter that projects MRS quantifiers into a first-order-style IR must explicitly interpret the qeq-connected restrictor structure and cannot treat `RSTR`/`BODY` as ordinary predicate arguments.

### Confidence

**Very high.**

### BLOCKED?

**No.**

---

## R4.2 Quantifier EP form and ERG 1214 quantifier inventory

### Standard structural form

ERG Semantics Basics states that all instance variables (`x`) are bound by generalized quantifiers. The normal quantifier EP has:

```text
quantifier_predicate
  ARG0: x
  RSTR: hR
  BODY: hB
```

and the nominal restrictor is connected through a `qeq` constraint.

Source:  
https://delph-in.github.io/docs/erg/ErgSemantics_Basics/

### Predicate naming

The DELPH-IN Predicate RFC documents surface predicates such as `_a_q` as quantifier predicates and distinguishes surface predicates from abstract predicates.

Source:  
https://delph-in.github.io/docs/tools/PredicateRfc/

The `_q` field is part of the standard surface-predicate naming convention for quantificational predicates; abstract quantifiers such as `udef_q` also use the `q` naming pattern.

### ERG 1214 predicate hierarchy

The actual ERG 1214 file:

`etc/hierarchy.smi`

contains, among others:

```text
_all_q       < universal_q
_each_q      < universal_q
_every_q     < every_q
every_q      < universal_q

_a_q         < some_q
_some_q      < some_q
some_q       < existential_q

_any_q       < existential_q
udef_q       < existential_q
proper_q     < existential_q
pronoun_q    < existential_q
number_q     < existential_q

_most_q      < abstract_q
_half_q      < abstract_q
```

Locator:  
https://github.com/delph-in/erg/blob/1214/etc/hierarchy.smi

### Meaning caution

The hierarchy supports robust **class membership** statements, e.g. `udef_q` is typed under `existential_q`, while `_all_q` is under `universal_q`. It does **not** by itself provide a full truth-conditional definition of `_most_q`; `_most_q` is classified under `abstract_q`, so an adapter should not infer a detailed majority formula solely from the hierarchy.

### `bare_div_q_rel` versus actual 1214 gold records

The actual DeepBank 1.1 cardinal records found in R2 use **`udef_q`**, not `bare_div_q_rel`. Thus, for an ERG-1214/DeepBank adapter, `udef_q` is the concrete form evidenced by the corpus items reported here. Formalism examples from other ERG vintages should not be substituted for this observed release behavior.

### Confidence

**Very high** for the hierarchy and R2 behavior.

### BLOCKED?

**No.**

---

## R4.3 Scope underspecification and whether gold gives one resolved scope

### Fact 1 — MRS itself is intentionally underspecified

The MRS RFC explicitly describes MRS as supporting scope underspecification. Quantifier scope can therefore remain unresolved in an MRS through handles and qeq constraints.

Source:  
https://delph-in.github.io/docs/tools/MrsRFC/

### Fact 2 — Redwoods gold selects an ERG analysis, not necessarily a fully scoped logical form

Redwoods documentation says an annotator decides which ERG **reading/analysis** is preferred in context.

Sources:

- https://delph-in.github.io/docs/garage/RedwoodsTop/
- https://www.nb.no/sprakbanken/en/resource-catalogue/oai-clarino-uib-no-eng-redwoods/

But an ERG analysis contains an MRS, and the MRS can still leave genuine quantifier-scope alternatives unresolved. Therefore these two facts are compatible:

1. one syntactico-semantic ERG analysis is selected as gold;
2. multiple fully scoped resolutions can still satisfy that selected MRS.

### Evidence from the actual R1/R2 records

The concrete records retain unconstrained `BODY` handles and qeq constraints. For example, R1 has:

```text
_most_q ... RSTR: h5 BODY: h7
HCONS: < h5 QEQ h8 ... >
```

The MRS does not replace that structure with one fully nested generalized-quantifier formula.

### Scope-solving tools

**Utool** describes itself as a tool/library for computations on underspecified semantic representations and ambiguity structures:

https://github.com/coli-saar/utool

A scope solver can enumerate resolved scopings compatible with an underspecified MRS. Such solver output is a **derived resolution set**. No evidence was found in the inspected Redwoods/DeepBank materials that one of those resolved scopings is separately chosen by a human annotator as the unique scope gold for every item.

### DMRS/EDS caution

DMRS and EDS are reductions/alternate views of MRS structure. Conversion to them is not evidence that a human-selected quantifier-scope resolution has been supplied. They should not be treated as a substitute for scope resolution merely because they are graph-shaped.

### Answer to R4.3

**Observed case: (b).** A Redwoods gold record can remain scope-underspecified. The human gold decision selects the ERG analysis; it does not, on the evidence recovered here, guarantee one fully scoped quantifier ordering.

### Confidence

**High.**

### BLOCKED?

- Whether **every** candidate item used by the project has more than one compatible scope: not tested here.
- Whether a separate hidden/discontinued Redwoods artifact contains human-selected resolved scopings: **BLOCKED / no evidence found**.
- General claim that MRS gold can remain underspecified: **not blocked**.

---

## R4.4 Negation

### Fact

ERG Semantics Basics classifies `not` among scopal operators: handle-valued arguments are scopal arguments, and negation belongs to that class.

Source:  
https://delph-in.github.io/docs/erg/ErgSemantics_Basics/

The ERG EDS/MRS documentation further states that, in an ERG-compliant MRS, the argument of negation is **scopal**.

Source:  
https://delph-in.github.io/docs/tools/EdsGeneration/

### Adapter implication

The direct structural analogue of the project IR’s `not` is therefore a scopal negation EP whose argument is a handle/scopal substructure. The exact predicate spelling can vary by serialized view (`neg`, `neg_rel` conventions), so the adapter should use the SEM-I / predicate inventory of the target ERG release rather than a string-only heuristic.

### Confidence

**High.**

### BLOCKED?

**No** for the structural fact.

---

## R4.5 Conditionals / implication

### ERG 1214 grammar evidence

The ERG semantic inventory explicitly lists:

```text
Conditionals: if_x_then
```

Source:  
https://delph-in.github.io/docs/erg/ErgSemantics_Inventory/

In the actual ERG 1214 grammar source, `lexrules.tdl` introduces:

```text
PRED "_if_x_then_rel"
ARG1 #main
ARG2 #subord
```

Locator:  
https://github.com/delph-in/erg/blob/1214/lexrules.tdl

The ERG 1214 `fundamentals.tdl` definition of `subord_relation` constrains **both `ARG1` and `ARG2` to be handles**:

```text
subord_relation := arg12_relation &
  [ ARG1 handle,
    ARG2 handle ].
```

Locator:  
https://github.com/delph-in/erg/blob/1214/fundamentals.tdl

### Adapter-relevant fact

The conditional is therefore represented as a two-place **scopal relation over handles**. The grammar source labels the two values `#main` and `#subord`.

### Direction caution

The inspected source names strongly suggest that the subordinate *if*-clause and matrix/main clause occupy different scopal arguments, but this report does not convert that naming into a formal `antecedent → consequent` rule without an item-level ERS example explicitly confirming argument direction. For a production adapter, direction should be fixed from a documented example/test, not guessed from argument order.

### Confidence

- Existence and handle-valued ARG1/ARG2: **Very high**
- Exact logical implication direction from argument position alone: **not asserted**

### BLOCKED?

**Partial** only for the final antecedent/consequent mapping convention.

---

# R5 — Access, format, and scale

## R5.1 Actual/historical release paths

### Official release identification

Official Redwoods page:

https://delph-in.github.io/docs/garage/RedwoodsTop/

It identifies Ninth Growth / ERG 1214 and describes the data as [incr tsdb()] treebanks.

### ERG 1214 tag

A currently accessible public GitHub view of the ERG 1214 tag is:

```text
https://github.com/delph-in/erg/tree/1214/tsdb/gold
```

This exposes profile directories and metadata files.

The historical DELPH-IN/SVN-style locator associated with the release was:

```text
http://svn.delph-in.net/erg/tags/1214/tsdb/gold
```

The exact literal path was attempted before alteration. Current browsing did not recover the payload through that historical endpoint; this is treated as an **access failure**, not as proof that the release never existed.

### DeepBank 1.1 semantic-graph historical path

A contemporary DELPH-IN discussion points to:

```text
http://sdp.delph-in.net/index.php?page=5
```

for “semantic graphs from DeepBank 1.1 (ERG 1214)”.

Both the exact `http` URL and its `https` variant timed out in the current web environment. This is recorded as `BLOCKED`, not a 404/absence finding.

### Evidence-copy mirror used for R1/R2

```text
https://github.com/Ayden666/L98Project/tree/6b07252aa1b0d349eba97ab68c388a65be895c02/DeepBank1.1
```

This is a third-party export mirror, not the rights authority.

### Confidence

**High** on the documented paths and current access outcomes.

---

## R5.2 Registration/license agreement

### ERG source / GitHub profile material

The public ERG GitHub repository is accessible without account-specific corpus registration. The grammar itself is MIT-licensed, but the grammar license is **not** used to infer source-text licenses.

Official grammar catalogue:  
https://delph-in.github.io/docs/grammars/GrammarCatalogue/

### WSJ/DeepBank data

For the SemEval-2015 SDP distribution derived from PTB/LDC materials, the official task page says participants needed to sign an LDC license agreement before obtaining the data.

Source:  
https://alt.qcri.org/semeval2015/task18/index.php?id=data-and-tools

For the historical full DeepBank 1.1 MRS export endpoint, the current access/registration state could not be verified because the endpoint timed out.

### BLOCKED

**Yes** for current official access conditions to the full DeepBank 1.1 MRS export.

---

## R5.3 [incr tsdb()] profile format and MRS extraction

### Native format

DeepBank documentation describes native HPSG analyses as **[incr tsdb()] profiles**, essentially flat-file relational databases.

Source:  
https://delph-in.github.io/docs/garage/DeepBank_OneZero/

The GitHub ERG 1214 `tsdb/gold` tree exposes typical profile files such as:

- `relations`
- `analysis`
- `item-*`
- `parameter`
- `rule`
- `score`
- `output`
- etc.

The exact populated tables vary by checked-in profile and distribution method.

### Standard Redwoods export

Official [incr tsdb()] export documentation supports selected active-tree export into formats including:

- `mrs`
- `indexed`
- `prolog`
- `mrx`
- `eds`
- derivation/tree formats

and documents the configuration:

```text
(setf tsdb::*redwoods-export-values*
      '(:derivation :tree :mrs :prolog))
```

Source:  
https://delph-in.github.io/docs/tools/ItsdbTreebanking_ItsdbExporting/

For WeScience, DELPH-IN gives an explicit Redwoods command example:

```text
./redwoods --binary --erg --target /tmp/wescience \
  --export derivation,tree,mrs,eds ws01
```

Source:  
https://delph-in.github.io/docs/garage/WeScience/

### PyDelphin

Current PyDelphin documentation supports:

- reading/selecting [incr tsdb()] profiles,
- `delphin mkprof`,
- `delphin process`,
- processing profiles with ACE,
- reading MRS results,
- converting DELPH-IN semantic formats.

Source:  
https://pydelphin.readthedocs.io/en/latest/guides/commands.html

A particularly relevant documented ERG-1214 example is:

```text
delphin process -g erg-1214-x86-64-0-9.27.dat mrs-parsed
```

### ACE

ACE can output MRS for parsed input and is supported directly by PyDelphin.

Sources:

- https://delph-in.github.io/docs/tools/AceUse/
- https://pydelphin.readthedocs.io/en/latest/api/delphin.ace.html

### Important preservation rule

Re-parsing the raw sentence with ACE is **not equivalent to retrieving the original gold MRS**, because current parser ranking or grammar versions can choose another analysis. For gold extraction, use the selected tree/result from the treebank profile/export, with the matching ERG version when reconstruction is required.

### Confidence

**High.**

---

## R5.4 Scale signal

### Corpus scale

Official Redwoods documentation says the preceding Eighth Growth already contained about **85,000 sentences** across multiple domains. Ninth Growth adds/improves DeepBank and uses ERG 1214.

Source:  
https://delph-in.github.io/docs/garage/RedwoodsTop/

DeepBank documentation describes a WSJ corpus on the order of **50,000 sentences**, with most first-release data receiving at least two rounds of human annotation.

Source:  
https://delph-in.github.io/docs/garage/DeepBank/

### Quantifier-item scale signal

This round did **not** perform a corpus-wide exact census. The evidence obtained is sufficient only for these lower bounds:

- proportional `_most_q`: **at least 1 directly inspected active DeepBank 1.1 record**
- exact cardinal `card(CARG N)`: **at least 3 directly inspected active DeepBank 1.1 records**

Repository search surfaced additional cardinal and `_most_q` hits, but they were not all manually classified against the project’s exclusion rules, so no larger count is reported as fact.

### Confidence

**High** for the confirmed lower bounds.  
**No claim** of corpus-wide counts.

### BLOCKED?

Exact/reliable release-wide eligible-count estimate remains **BLOCKED until a machine census is run**.

---

# R6 — Alternative DELPH-IN gold treebank

The request specified R6 **only if R1 ended BLOCKED**.

R1 did not end BLOCKED: a concrete DeepBank/Redwoods `_most_q` active record was located. Therefore no replacement DELPH-IN source was promoted under R6.

**Status:** Not triggered by the request’s own condition.

---

# Cross-check: paper/formalism examples versus corpus items

To obey the Round-3 requirement, the following facts are kept distinct:

| Claim type | Evidence used |
|---|---|
| MRS can represent generalized quantifiers with `RSTR/BODY` | MRS RFC + ERG Semantics documentation |
| ERG 1214 knows `_most_q`, `udef_q`, etc. | actual ERG 1214 `etc/hierarchy.smi` |
| DeepBank corpus actually contains proportional `_most_q` | concrete item `20214052` |
| DeepBank corpus actually separates cardinal and quantifier EPs | concrete items `21438006`, `21618050`, `20725062` |
| Redwoods is human-selected gold | official Redwoods/CLARINO methodology |
| One fully resolved quantifier scope is human-gold | **not established**; MRS remains underspecified |
| Redwoods metadata says GPL | CLARINO metadata |
| All source texts are GPL | **not established; contradicted by component rights such as WSJ** |

---

# BLOCKED and failed-path ledger

| Requested fact/path | Attempt | Outcome |
|---|---|---|
| Official full DeepBank 1.1 MRS item download | historical SDP endpoint `http://sdp.delph-in.net/index.php?page=5` | timeout |
| Same endpoint with HTTPS | `https://sdp.delph-in.net/index.php?page=5` | timeout |
| Historical ERG 1214 SVN gold path | literal historical path tried before correction/substitution | payload not recovered in current browser; not treated as absence |
| Official current item-level full-MRS view for `20214052` | DELPH-IN docs + ERG 1214 GitHub tag searched | release/profile structure confirmed, but direct official full MRS record not recovered |
| Item-level MRS evidence | third-party DeepBank1.1 Redwoods export mirror | recovered successfully; used only as evidence copy |
| Exact full DeepBank 1.1 MRS export license | official Redwoods, DeepBank, SDP/LDC paths searched | not found as a dataset-specific statement; `BLOCKED` |
| Ninth-Growth component licenses | official Redwoods inventory + inspected ERG tag profiles | `ws01` explicit CC BY-SA 3.0 found; several other component-specific rights remain `BLOCKED` |
| `cb` component license in ERG 1214 profile | inspected `tsdb/gold/cb`; direct `cb/LICENSE` attempt | no `LICENSE` present at that path; no absence claim about external source rights |
| Human-selected fully scoped quantifier gold | Redwoods methodology + MRS RFC + scope tooling searched | no evidence found; selected MRS remains capable of underspecification |
| Exact corpus-wide count of eligible `_most_q` / cardinal records | search only, no complete census | not measured; only confirmed lower bounds reported |

---

# Source register

## Official / primary documentation

- DELPH-IN Redwoods Treebank  
  https://delph-in.github.io/docs/garage/RedwoodsTop/

- CLARINO/Språkbanken Redwoods metadata copy  
  https://www.nb.no/sprakbanken/en/resource-catalogue/oai-clarino-uib-no-eng-redwoods/

- DELPH-IN DeepBank  
  https://delph-in.github.io/docs/garage/DeepBank/

- DELPH-IN DeepBank 1.0  
  https://delph-in.github.io/docs/garage/DeepBank_OneZero/

- MRS RFC  
  https://delph-in.github.io/docs/tools/MrsRFC/

- ERG Semantics Basics  
  https://delph-in.github.io/docs/erg/ErgSemantics_Basics/

- ERG Semantic Inventory  
  https://delph-in.github.io/docs/erg/ErgSemantics_Inventory/

- ERG Predicate RFC  
  https://delph-in.github.io/docs/tools/PredicateRfc/

- ERG 1214 predicate hierarchy  
  https://github.com/delph-in/erg/blob/1214/etc/hierarchy.smi

- ERG 1214 `lexrules.tdl`  
  https://github.com/delph-in/erg/blob/1214/lexrules.tdl

- ERG 1214 `fundamentals.tdl`  
  https://github.com/delph-in/erg/blob/1214/fundamentals.tdl

- ERG 1214 gold-profile tree  
  https://github.com/delph-in/erg/tree/1214/tsdb/gold

- Redwoods [incr tsdb()] export documentation  
  https://delph-in.github.io/docs/tools/ItsdbTreebanking_ItsdbExporting/

- WeScience export documentation  
  https://delph-in.github.io/docs/garage/WeScience/

- PyDelphin command-line documentation  
  https://pydelphin.readthedocs.io/en/latest/guides/commands.html

- PyDelphin [incr tsdb()] guide  
  https://pydelphin.readthedocs.io/en/latest/guides/itsdb.html

- ACE use documentation  
  https://delph-in.github.io/docs/tools/AceUse/

- SemEval 2015 Task 18 data and licensing  
  https://alt.qcri.org/semeval2015/task18/index.php?id=data-and-tools

- LDC ACL/DCI WSJ-containing release  
  https://catalog.ldc.upenn.edu/LDC93T1

## Concrete item evidence copy

These are **third-party mirror locators**, not rights authorities:

- `20214052` — proportional `_most_q`  
  https://github.com/Ayden666/L98Project/blob/6b07252aa1b0d349eba97ab68c388a65be895c02/DeepBank1.1/20214052

- `21438006` — exact cardinal 3  
  https://github.com/Ayden666/L98Project/blob/6b07252aa1b0d349eba97ab68c388a65be895c02/DeepBank1.1/21438006

- `21618050` — exact cardinal 2  
  https://github.com/Ayden666/L98Project/blob/6b07252aa1b0d349eba97ab68c388a65be895c02/DeepBank1.1/21618050

- `20725062` — exact cardinal 5  
  https://github.com/Ayden666/L98Project/blob/6b07252aa1b0d349eba97ab68c388a65be895c02/DeepBank1.1/20725062

---

# Handoff facts for the operating session

Without making an eligibility decision, the machine-measurement handoff can rely on the following verified facts:

1. `20214052` supplies one actual DeepBank/Redwoods proportional quantifier record with `_most_q(ARG0, RSTR, BODY)`.
2. `21438006`, `21618050`, and `20725062` supply three actual exact-cardinal records with `card(CARG N)` **separate** from `udef_q(RSTR,BODY)`.
3. The Redwoods human gold decision is a selected ERG analysis, but MRS quantifier scope can remain qeq-underspecified; a unique human-selected fully scoped logical form was **not** established.
4. The located items are all in the WSJ/DeepBank component. Redwoods-level GPL metadata does not eliminate WSJ/LDC/Dow Jones source-text restrictions.
5. The exact license of the **full DeepBank 1.1 MRS export** remains `BLOCKED`; do not substitute the ERG MIT license, DeepBank 1.0 META-SHARE license, or SemEval reduced-graph LDC agreement for that missing statement.
6. Corpus-wide eligible-item counts were not measured in this research round; only the concrete lower bounds above are asserted.

<!-- VERBATIM-END -->

---

# B. 운영 세션 수신 검증 (2026-08-24)

## B.0 검증 설계 — 무엇을 어떤 근거로 판정하는가

**전제(사용자 지시)**: 조사 agent(openai_web_gpt)와 이 세션의 도구 권한이
다르고, **이 세션의 웹 도달 권한이 더 넓다**(§11.6 실측: openai_web_gpt는
`application/zip` 열기 불가·대용량 fetch 제한). 따라서 검증의 방향은 두 가지다.

1. 회신이 `BLOCKED`로 남긴 경로를 **내가 직접 뚫는다** — 회신의 BLOCKED를
   "부재"로 읽지 않는다(요청서 §3-3 원칙). 뚫리면 그것은 회신의 오류가 아니라
   **권한 차이의 결과**로 기록한다.
2. 내가 도달하지 못한 것은 **`BLOCKED_FOR_VERIFIER`** 로 표시한다 — 회신을
   반증한 것이 아니다(저장소 PASS/FAIL/BLOCKED 어휘와 동일 규약).

| 축 | 무엇을 판정 | 근거(내가 실제로 쓸 수 있는 것) |
|---|---|---|
| V1 | 인용된 MRS 조각이 실물과 일치하는가 | mirror 4건 직접 다운로드 후 원문 대조 |
| V2 | 회신의 BLOCKED가 내 권한으로 뚫리는가 | timeout 처리된 공식 엔드포인트 직접 요청 |
| V3 | 방언 8종으로 표현 가능한가 | `cg_ir.validate_formula` + 생성 스키마 |
| V4 | 표면 필터·투영 신호 게이트를 통과하는가 | `_stage2_surface_filters` · `projection_signal_check` |
| V5 | D-29 §11 fail-closed 조건을 실물이 만족하는가 | 실물 MRS의 RSTR/BODY·HCONS 판독 |
| V6 | D-29 §13 뮤테이션 5종이 실물로 실행 가능한가 | 실물의 `rel` 분포 |
| V7 | 선행 판정·배제 목록과 충돌하는가 | D-21·D-29·요청서 §0 대조 |

## B.1 V1 — 인용 대조: **4/4 CONFIRMED**

mirror 4건을 직접 받았다(HTTP 200, 3,616 / 8,985 / 4,069 / 4,444 bytes).
회신이 인용한 조각이 원문과 일치한다.

| item | profile | 상태 | 실물 확인 |
|---|---|---|---|
| `20214052` | `wsj02a` | `[20214052:0] (active)` | `_most_q<0:4>` `RSTR: h5` `BODY: h7` · `generic_entity<0:4> LBL: h8` · `HCONS: < h5 QEQ h8 h1 QEQ h2 >` |
| `21438006` | `wsj14b` | `(active)` | `udef_q<0:5> RSTR: h6 BODY: h7` · `card<0:5> … CARG: "3"` · `_company_n_of<6:15>` |
| `21618050` | `wsj16b` | `(active)` | `udef_q<0:3> RSTR: h6 BODY: h7` · `card<0:3> CARG: "2"` · `_irony_n_1<4:11>` |
| `20725062` | `wsj07a` | `(active)` | `udef_q<0:5> RSTR: h7 BODY: h8` · `card<0:5> CARG: "5"` · `generic_entity<0:5>` |

표면 문장도 확인됐다(토큰 표 실물): `Most / are / trim / .` 등.

**회신이 말하지 않은 구조 사실 1건 추가(실물에서만 보인다)**:
`card`와 명사 술어가 **같은 LBL을 공유**한다(`21618050`: `card<0:3> LBL: h8`,
`_irony_n_1<4:11> LBL: h8`). 즉 `card`는 quantifier의 **제한식 내부 술어**이고
독립 결박자가 아니다. 그리고 `card`의 `ARG0`은 **사건 변수**(`e9`, TENSE
UNTENSED)다. 이는 D-29 §9의 "같은 결박 변수로 연결될 때만 package"를
**강화한다** — attachment 판정은 `ARG1`↔`BV` 동일성뿐 아니라 **LBL 공유**를
읽어야 한다. `MRS_COUNT_PROJECTION_V1` 구현 시 이 사실이 필요하다.

## B.2 V2 — 회신의 BLOCKED를 권한 차이로 뚫었다: **2건 해소**

### B.2.1 공식 SDP 엔드포인트 — 회신 "timeout" → 내 실측 **HTTP 200**

회신의 BLOCKED 원장 첫 두 행은
`http://sdp.delph-in.net/index.php?page=5`(그리고 https)를 timeout으로 기록했다.
내 실측: **http는 HTTP 200 / 4,736 bytes**(https는 실패 — 회신의 관측과 일치).
즉 **프로토콜 하나만 살아 있다.** 회신이 https도 시도한 것은 정확했고,
http에서의 실패는 그쪽 환경의 제약이었다.

그 페이지가 회신이 `BLOCKED`로 남긴 라이선스 항목에 직접 답한다(verbatim):

> "One of the four English target representations (viz. DM) and the entire Czech
> data (in the PSD target representation) are **not derivative of LDC-licensed
> annotations** and, thus, can be made available for **direct download (Open SDP;
> version 1.2; January 2017)** under a more permissive licensing scheme, viz. the
> Creative Commons Attribution-NonCommercial-ShareAlike license (**CC BY-NC-SA 2.0**).
> This package also includes some 'richer' meaning representations from which the
> English bi-lexical DM graphs derive, viz. **scope-underspecified logical forms
> (in the framework of Minimal Recursion Semantics; MRS)**"

### B.2.2 그 묶음의 실물 위치·크기·라이선스를 확보했다

`http://sdp.delph-in.net/osdp-12.tgz` → 302 → `hdl.handle.net/11234/1-1956`
→ **LINDAT/CLARIN**(Charles University) DSpace.

| 항목 | 실측값 |
|---|---|
| 직접 다운로드 | `https://lindat.mff.cuni.cz/repository/server/api/core/bitstreams/4cc9fc88-da2a-47ee-95a8-d7a1c4c20fa8/content` |
| 헤더 | `HTTP 200` · `application/x-gzip` · **397,685,740 bytes** |
| 파일명 | `osdp-12.tgz` (부속 `semeval15.pdf`, 1,665 B bitstream 1건) |
| handle | `11234/1-1956` |
| 리포지터리 라이선스 표기 | **CC BY-NC-SA 4.0** (`clarinlicenses` 이름) |

**불일치 1건을 그대로 기록한다**: SDP 페이지는 **2.0**, LINDAT 메타데이터는
**4.0**이다. 어느 쪽이 이 묶음의 정본인지는 판정하지 않는다 — 두 표기 모두
실물 인용이고, 조용히 하나로 통일하면 라이선스를 추정하는 것이 된다
(요청서 §3-1 "라이선스를 정책으로 추정 금지").

**의미**: 회신이 `BLOCKED`로 남긴 것은 "DeepBank 1.1 **full MRS export**의
데이터 특정 라이선스"였고 그 BLOCKED는 **여전히 유효하다**. 내가 찾은 것은
**다른 artifact**다 — MRS를 포함한다고 공식 페이지가 진술하고, 라이선스가
명시되며, **직접 다운로드가 가능한** 379MB 묶음. 이것은 제3 source 경로를
`GPL 주장 + 제3자 mirror + BLOCKED 라이선스`에서 **명시 라이선스 + 공식 배포처**로
바꿀 수 있는 후보다. 단 **NC(비상업)·SA(동일조건변경허락)** 제약이 붙는다.

## B.3 V3~V4 — 우리 계약으로의 기계 실측

방언 8종 표현 가능성: **4/4 통과**(`cg_ir.validate_formula` 무오류 +
생성 스키마 검증 통과). 예:
`prop(most, x, generic_entity(x), trim(x))` ·
`count(eq, 3, x, company(x), begin_trading(x))`.

투영 신호 게이트: 실측이 **우리 쪽 결함**을 적발했다 —
`projection_signal_check`가 target 양화를 `forall|exists`로만 세어
기수·비례 4건 전부 `target_quantifiers=0` → `SIGNAL_COLLAPSED`였다.
fail-closed라 안전 쪽으로 틀렸지만 **이유가 틀렸다**(신호 붕괴가 아니라
게이트의 시야 부족). `TARGET_BINDERS`로 명시 집합을 도입해 수리했고,
**게이트를 무르게 하지 않았음을 음성 테스트로 결박**했다(본문이 `True`인
count는 여전히 `SIGNAL_COLLAPSED`). 수리 후 4/4 `SIGNAL_RETAINED`.
실험 스위트 206 passed.

## B.4 V5 — D-29 §11 fail-closed 조건이 실물을 **전부 거부한다** (중대)

판정 §11은 `require: RSTR_resolved: true, BODY_resolved: true`와
`reject_if: unresolved_handle_constraint`를 명한다. 실물 판독:

| item | RSTR | HCONS가 RSTR을 묶는가 | BODY | HCONS가 BODY를 묶는가 |
|---|---|---|---|---|
| `20214052` | `h5` | **예** (`h5 QEQ h8`) | `h7` | **아니오** |
| `21438006` | `h6` | 예 (`h6 QEQ h8`) | `h7` | **아니오** |
| `21618050` | `h6` | 예 (`h6 QEQ h8`) | `h7` | **아니오** |
| `20725062` | `h7` | 예 (`h7 QEQ h4`) | `h8` | **아니오** |

**4/4에서 BODY handle이 HCONS에 등장하지 않는다.** 이것은 결함 있는 record가
아니라 MRS의 정상 형태다 — 최외곽 양화의 BODY는 scope resolution 단계에서
채워지도록 비워 둔다(회신 R4.3이 같은 사실을 인용으로 확인).

따라서 §11을 문자 그대로 구현하면 **모든 MRS record가 거부된다.** 이는
D-25가 금지한 "실패가 예정된 계약을 실행하는 것"과 동형이다.
동시에 **조용히 완화해서도 안 된다**(P19: 내 범위 조정 권고는 3연속 기각됐다).

관측된 완화 후보를 **판정 상신용으로만** 적어 둔다 — 채택하지 않았다:
단일 양화 문장에서 BODY는 비묶임이지만 **유일하게 결정된다**(남은 label이
`TOP h1 QEQ h2`의 `h2` 하나뿐). 즉 `BODY_resolved`를 "제약됨"이 아니라
**"유일 해소 가능"** 으로 읽으면 4/4가 통과하고, 다중 양화에서는 여전히
거부된다(그때가 진짜 scope 미명세다). 이 독법이 옳은지는 **판정 사안**이다.

## B.5 V6 — 뮤테이션 5종 중 1종은 실물 재료가 없다

회신이 찾아온 기수 3건의 `rel`은 **전부 `eq`**(정확 기수 3·2·5)이고, 회신도
"No lower-bound or upper-bound example is claimed here"라고 명시했다.

**그러나 corpus 전역에서는 다르다(§B.11 이후 실측, 이 절의 초판 결론을 정정).**
`card` 보유 13,470건에서 정도 수식 술어의 공기 분포:

| 술어 | 건수 | 우리 `rel`로의 함의 |
|---|---:|---|
| `_at+least_x_deg` | **156** | `ge` |
| `_over_p` | 269 | `gt`(전치사 용법 혼재 — 감사 필요) |
| `_under_p` | 177 | `lt`(동일) |
| `_more+than_p` | 62 | `gt` |
| `_about_x_deg` | 948 | 근사 — v1 방언 밖 |
| `_only_x_deg` | 298 | 초점 — 기수 관계 아님 |

즉 `ge`/`gt`/`lt` 재료가 **부재하지 않는다**. 초판이 "실물 자격 검사로는
공허"라고 쓴 것은 **회신의 3건이라는 표본에만** 타당했고 corpus로는 틀렸다.
정확한 미결 질문은 "재료가 없다"가 아니라 **"`at least three` 같은 정도
수식이 `card` 위에 얹힌 MRS를 `count(rel=ge)`로 사상하는 규칙이 아직 없다"**
이다 — D-29는 `card` 단독만 다뤘다. Q30.4를 그 형태로 고쳐 상신한다.

## B.6 V6b — 비례 재료의 구조적 문제: 유일한 1건이 **무어휘 제한식**이다

`20214052`(유일한 비례 record)와 `20725062`의 제한식은 `generic_entity`다 —
어휘 술어가 아니라 ERG의 무어휘 자리표다. subject는 `Most are trim.`을 받고
**제한식에 무엇을 쓸지 알 수 없다**(문장에 명사가 없다). 채점은 라벨을
익명화하므로 signature 비교 자체는 성립하지만, subject가 **제한식 노드를
만들어야 한다는 것 자체**를 문장에서 추론할 근거가 없다. 이는 G63/G68과 같은
계열(방언·라벨 도달성)이고, **비례 층의 하한 1건이 이 문제를 안고 있다**.

## B.7 V7 — 선행 판정·배제 목록 대조: 충돌 없음

- 요청서 §0의 배제 source(Wikisem 등)를 **재제안하지 않았다** — G87(2회
  반복된 우리 요청서 결함)에 대한 대응이 작동했다는 첫 증거다.
- 2차가 형식/예시 수준에서만 확립한 "card EP와 quantifier EP 분리"를
  **실제 corpus record로 승격**했다 — 2차 결론과 충돌하지 않고 강화한다.
- R6은 요청서의 조건(R1이 BLOCKED일 때만)을 지켜 발동하지 않았다. 준수 확인.
- 회신이 적격성 판정을 하지 않았다(명시적 진술 + 실제로 판정문 없음). 준수.

## B.8 D-29 §12 승격 선행 조건 대조 — **아직 승격 불가**

| 선행 조건 | 상태 | 근거 |
|---|---|---|
| proportional item locator 확보 | ✅ **충족** | `20214052` 실물 확인(B.1) |
| eligible cardinal ≥ 3 | ⚠️ **locator는 3건, 적격은 미판정** | 표현 가능·신호 보존은 통과(B.3); `rel` 단조(B.5)·권리(아래)가 남음 |
| eligible proportional ≥ 1 | ⚠️ **1건이나 B.6의 구조 문제** | 무어휘 제한식 |
| 실제 component/item의 rights 확인 | ❌ **미충족** | 4/4가 `wsj*` = WSJ/Dow Jones. LDC93T1 실물 확인: "Wall Street Journal Materials, Copyright 1987, 1988, 1989 Dow Jones Inc." **우리 저장소는 공개 GitHub이고 D-29 §17이 Gate C 대조표에 surface reading 열을 요구한다** — 즉 문장 원문이 커밋된다. (manifest 자체는 `text_sha256`만 저장하므로 manifest는 무해) |
| MRS→IR adapter qualification | ❌ 미착수 | adapter 본체 미구현 |
| card/prop attachment fail-closed qualification | ❌ **계약이 실물을 전부 거부**(B.4) | 판정 상신 필요 |
| (파생) 규모 신호 | ⚠️ 하한만 | 회신이 census 미수행을 명시 |

## B.9 이 검증이 만든 판정 상신 항목 (Q30 후보)

1. **`BODY_resolved`의 정의** — "HCONS에 제약됨"인가 "유일 해소 가능"인가.
   전자면 MRS source는 원리상 채택 불가다(B.4).
2. **`wsj*` 권리 하에서 surface reading을 저장소에 커밋할 수 있는가**, 아니면
   Gate C 대조표에서 문장 원문을 해시로 대체해야 하는가(B.8).
3. **Open SDP 1.2(CC BY-NC-SA)를 DeepBank 1.1 대신 배포처로 삼을 수 있는가** —
   NC·SA 제약이 사전등록 공개와 양립하는가. 라이선스 표기 2.0/4.0 불일치 포함(B.2.2).
4. **`count.rel`의 실물 미운동을 어떻게 회계하는가**(B.5) — `eq`만 있는 재료로
   `rel` 차원을 estimand에 유지하는 것이 정당한가.
5. **무어휘 제한식(`generic_entity`) fixture의 지위**(B.6).
6. **control 표면 어휘** — `UNSUPPORTED_QUANTIFIER_LEXICON`이 아직 `most`를
   담고 있고 기수어는 `SUPPORTED`에 없다. D-29가 방언을 넓혔으므로 이 표는
   사실과 어긋나지만, control 적격 의미론은 D-27이 정한 측정 계약이므로
   **운영 세션이 임의로 고치지 않았다**. 그대로 두면 적격성 스캔이 기수·비례
   층을 영원히 선별하지 못한다.

## B.10 이 검증의 한계

- **`BLOCKED_FOR_VERIFIER`**: Open SDP 1.2 묶음의 **내용**은 이 기록 시점에
  다운로드 진행 중이었다 — MRS가 실제로 그 안에 있고 우리 4건(또는 임의의
  비례·기수 record)을 포함하는지는 **미확인**이다. 공식 페이지의 진술만 근거다.
- mirror(제3자 GitHub)는 **item locator 및 구조 증거**로만 썼다. 권리 근거로
  쓰지 않았다 — 회신의 규율과 동일.
- LDC93T1 README의 "연구 그룹 밖 재배포 금지" 문구는 저작권 표기만 실물
  확인했고 재배포 조항 문구 자체는 이 세션에서 인용 확보하지 못했다
  (`BLOCKED_FOR_VERIFIER`). 회신의 인용을 반증하지 않는다.
- B.4의 완화 후보는 **제안이 아니라 관측**이다. 판정 없이 구현하지 않는다.

## B.11 전수 census — 회신이 BLOCKED로 남긴 규모 항목을 해소했다

회신 R5.4는 "release-wide 적격 건수는 machine census 없이는 BLOCKED"로 남겼다.
공식 Open SDP 1.2 묶음(§B.2.2)을 받아 **전수 실측**했다.

| 항목 | 실측값 |
|---|---|
| MRS record 총수 (`sdp/2015/eds/*.mrs.gz`) | **37,066** |
| `cg_mrs_reader`로 파싱 성공 | **37,060** (거부 6건 = 0.016%, 전부 fail-closed. 예상 밖 예외 0) |
| 양화 EP를 가진 record | 37,019 |
| `_most_q` 보유 record (비례) | **443** |
| 그중 양화가 **1개뿐**(BODY가 유일 해소되는 경우) | **3** |
| `card` 보유 record (기수) | **13,470** |
| **`MRS_COUNT_PROJECTION_V1` package 성공** | **0** |

거부 사유 분포(`card` 보유 record):

| 사유 | 건수 |
|---|---|
| `multiple_card_EP_candidates` | 7,755 |
| `unresolved_handle_constraint` | 4,064 |
| `unsupported_numeric_relation` | 1,077 |
| `card_and_quantifier_variable_disagree` | 574 |

### B.11.0 정정 — 앞서 적은 `6,154`는 깨진 도구의 수치였다

이 문서 초판에 `card` 보유 record를 **6,154**로 적었다. 그 값은 §B.11.3이
설명하는 **깨진 임시 정규식**에서 나왔고, 같은 표의 거부 사유 분포
(7,755+4,064+1,077+574 = **13,470**)와 **자기 모순**이었다. 계약 결박된
`cg_mrs_reader`로 재실측한 정본은 **13,470**이다. 표를 정정했다.
초판 수치를 지우지 않고 이 절에 남기는 이유: 같은 문서 안에서 합이 맞지
않는 두 수치가 공존했다는 사실 자체가 P16의 증거다.

### B.11.1 `BODY_resolved` 하나가 16,584건을 0건으로 만든다

attachment 단위(변수별 단일 `card` + 정수 `CARG` + 그 변수를 결박하는 양화 1개)로
다시 세면:

| 상태 | 건수 |
|---|---|
| 판정 §11 조건 **전부** 충족 | **0** |
| **BODY 비제약만이 유일한 장애** | **16,584** (100.0%) |
| RSTR·BODY 둘 다 비제약 | 3 |

즉 §B.4의 4건 관측은 우연이 아니고 **corpus 전역 성질**이다. `BODY_resolved`를
"HCONS에 제약됨"으로 읽는 한 MRS source의 적격 기수 재료는 **구조적으로 0건**이고,
그 한 조건만 "유일 해소 가능"으로 읽으면 **16,584건**이 된다. 이것이 Q30.1의
정확한 대가다.

### B.11.2 운영 세션이 계약에서 고른 해석 1건을 드러내 둔다 (Q30.7)

판정 §11의 `multiple_card_EP_candidates`를 나는 **문장 내 `card` EP가 둘 이상이면
거부**로 구현했다(v1 최소주의). 더 좁은 독법 — **같은 결박 변수에 대한 후보가
둘 이상일 때만 거부** — 도 문면에 부합한다("candidates"는 attachment 후보를
가리킬 수 있다). 이 선택이 **7,755건**을 좌우한다. 어느 독법이 정본인지 청한다.
지금 구현은 **좁지 않은 쪽(엄격)** 이고, 그 사실을 숨기지 않았다.

### B.11.3 이 census가 신뢰 가능한 이유 (그리고 한 번 틀렸던 이유)

첫 census는 **내 임시 정규식**으로 돌렸고 좁힌 수치(비례 16 / 기수 2 / 170)를
냈다. 그 도구는 **중첩 feature 구조에서 깨졌다** — `ARG0: x5 [ x PERS: 3 NUM: PL ]`
때문에 `udef_q`의 `RSTR`/`BODY`를 못 봤고, 그래서 양화를 세지 못했다. 실물로
재현 확인 후 그 수치를 **전량 폐기**했다. 위 표는 계약 17건으로 결박된
`cg_mrs_reader`(feature 구조 건너뛰기가 계약 항목)로 다시 돌린 것이다.
**검증 도구의 산출보다 검증 도구의 작동을 먼저 검증하라**(P16)의 재실증이다.
