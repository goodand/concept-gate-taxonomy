# Experiment Validation Pipeline

- `experiment-validation-pipeline.mmd` is the canonical Mermaid source.
- `experiment-validation-pipeline.svg` is the current confirmed render exported from the official Mermaid paid site on 2026-08-11.
- `runtime-module-architecture.mmd` is the canonical source for the six-module runtime architecture.
- `runtime-module-architecture.svg` is its current confirmed render exported from the official Mermaid paid site on 2026-08-11.

The validation pipeline presents execution order. The runtime architecture presents module and evidence boundaries. Neither diagram replaces the experiment contract, preregistration, qualification artifacts, authorization record, or audit evidence.

The SVG exports include the audit-input gate and packet-only reviewer trust boundary defined by the canonical MMD sources.

## As-built status (2026-08-11, Amendment 36)

Independent review round 15 asked whether these diagrams describe the code or
a target. Both nodes it questioned are now implemented:

| Diagram node | Implemented by | Enforced |
|---|---|---|
| `Audit Input Gate` | `validate_audit_input` against `safety_audit_spec.json` | kind, exact case x arm matrix, allowed variants, cell count, duplicate keys, result<->trace bijection **both directions** |
| `Isolated Blind Review Boundary` | packet written to `audit_workspace/<stem>/`, key to `results/` | the reviewer directory contains `packet.json` and nothing else |
| `Trusted Post-run Evaluation` | builder + adjudicator run outside the reviewer workspace | reviewer never receives key, result, or automatic scores |

Before Amendment 36 the pipeline diagram was ahead of the code: it drew an
audit input gate that did not exist, so a 1-cell, non-primary artifact could
build a packet. That is recorded here rather than quietly corrected, because
"the diagram was aspirational" is exactly the failure mode a validation
diagram should not have.

**Still a target, not as-built**, and deliberately so:

- `Independent Reviewers` in the runtime diagram means **distinct declared
  reviewer IDs**. Physical independence -- two different people, who did not
  confer -- is procedural and is NOT machine-verified. See
  `SAFETY_AUDIT_RUBRIC.md`.
- The runtime diagram shows Host Runtime, Providers, and the workflow gate as
  separate modules. In the code they still share `run_live_phase_c.py`
  (~1,340 lines). The boundaries the diagram draws are real as *evidence*
  boundaries; they are not yet file boundaries.

