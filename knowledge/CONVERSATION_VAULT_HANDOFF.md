# Conversation vault handoff

This directory is the Git-versioned knowledge entrypoint for agents operating
from another PC, workspace, or session. It preserves the conversation-derived
project map, canonical notes, typed semantic edges, searchable indexes, and
symlink classification views.

## Read order

1. `files/markdown/vault-readme.md`
2. `files/markdown/moc-ontology-reasoner-mcp.md`
3. `files/markdown/moc-vault-architecture.md`
4. `files/jsonl/manifest.jsonl`
5. `files/jsonl/edges.jsonl`
6. `files/text/validation-report.txt`
7. `../docs/HANDOFF.md` for the live branch-specific E2 experiment state

## Authority and status

- `files/` is canonical storage; the other top-level directories are navigation
  views implemented as relative symlinks.
- `manifest.jsonl` maps stable IDs to canonical paths and SHA-256 hashes.
- `edges.jsonl` is the typed relation ledger. Use only `accepted` edges as
  established relations.
- Markdown wikilinks are human navigation aids and do not replace the typed
  edge ledger.
- The snapshot records E2.3 as `screened`, not confirmed, and E2.4 as
  `design-only`, not executed.
- The available conversation source is explicitly partial. Missing earlier
  turns must remain unknown rather than being inferred as source text.

## Updating

Edit canonical files under `files/`, then run:

```bash
python3 scripts/build-vault.py --check
```

Commit regenerated indexes and relative symlinks together with the canonical
changes. Keep symlinks as symlinks; copying their targets into view directories
creates duplicate authority.

## Snapshot provenance

- Generated: 2026-07-26
- Project: `goodand/concept-gate-taxonomy`
- Base branch at publication: `codex/e2.4-contract-repo-design`
- Vault validation result at publication: `PASS`
