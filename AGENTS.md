# Agent entrypoint

This repository includes a versioned conversation knowledge vault for agents
working from another PC, workspace, or session.

When a request depends on project history, experiment decisions, ontology
terminology, or prior evidence, read these files before acting:

1. `knowledge/CONVERSATION_VAULT_HANDOFF.md`
2. `knowledge/conversation-vault/files/markdown/vault-readme.md`
3. `knowledge/conversation-vault/files/markdown/moc-ontology-reasoner-mcp.md`
4. `knowledge/conversation-vault/files/jsonl/manifest.jsonl`
5. `knowledge/conversation-vault/files/jsonl/edges.jsonl`
6. `knowledge/conversation-vault/files/text/validation-report.txt`

Interpretation rules:

- Treat `files/` as canonical storage.
- Treat `views/`, `graph/`, `schemas/`, `manifests/`, `scripts/`, and the
  vault-level `README.md` as symlink-based navigation views.
- Treat only edges whose `review_status` is `accepted` as established graph
  relations.
- Preserve the recorded status distinction: E2.3 is `screened`; E2.4 is
  `design-only` in this vault snapshot.
- Conversation source coverage is partial. Do not reconstruct omitted messages
  or turn summaries as verbatim source material.
- For the branch's live E2 experiment state, also read `docs/HANDOFF.md`. When
  it differs from the vault snapshot, report the dated conflict instead of
  silently overwriting either source.

To validate or regenerate the vault after editing canonical files:

```bash
python3 knowledge/conversation-vault/scripts/build-vault.py --check
```
