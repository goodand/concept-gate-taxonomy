#!/usr/bin/env python3
"""Build and validate generated views for the conversation knowledge vault."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import yaml


VAULT = Path(__file__).resolve().parents[2]
FILES = VAULT / "files"
ARTIFACTS_PATH = FILES / "json" / "artifacts.json"
NODE_TYPES_PATH = FILES / "json" / "node_types.json"
RELATION_TYPES_PATH = FILES / "json" / "relation_types.json"
EDGES_PATH = FILES / "jsonl" / "edges.jsonl"
MANIFEST_PATH = FILES / "jsonl" / "manifest.jsonl"
KEYWORD_INDEX_PATH = FILES / "jsonl" / "keyword_index.jsonl"
NODES_CSV_PATH = FILES / "csv" / "nodes.csv"
EDGES_CSV_PATH = FILES / "csv" / "edges.csv"
KEYWORD_EDGES_CSV_PATH = FILES / "csv" / "keyword_edges.csv"
BACKLINK_PATH = FILES / "markdown" / "backlink-index.md"
REPORT_PATH = FILES / "text" / "validation-report.txt"


class VaultError(RuntimeError):
    pass


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VaultError(f"cannot read JSON {path.relative_to(VAULT)}: {exc}") from exc


def load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise VaultError(f"cannot read JSONL {path.relative_to(VAULT)}: {exc}") from exc
    for lineno, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise VaultError(f"invalid JSONL {path.relative_to(VAULT)}:{lineno}: {exc}") from exc
    return records


def discover_nodes() -> list[dict]:
    nodes: list[dict] = []
    for path in sorted((FILES / "markdown").glob("*.md")):
        if path == BACKLINK_PATH:
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            raise VaultError(f"missing YAML frontmatter: {path.relative_to(VAULT)}")
        try:
            header = text.split("---\n", 2)[1]
            metadata = yaml.safe_load(header)
        except (IndexError, yaml.YAMLError) as exc:
            raise VaultError(f"invalid frontmatter: {path.relative_to(VAULT)}: {exc}") from exc
        if not isinstance(metadata, dict):
            raise VaultError(f"frontmatter must be a mapping: {path.relative_to(VAULT)}")
        node = dict(metadata)
        node["file"] = str(path.relative_to(VAULT))
        keywords = node.get("keywords", [])
        if not isinstance(keywords, list):
            raise VaultError(f"keywords must be a list: {path.relative_to(VAULT)}")
        node["topics"] = sorted({slugify(str(keyword)) for keyword in keywords if str(keyword).strip()})
        node.setdefault("source_scope", [])
        nodes.append(node)
    return nodes


def dump_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in records),
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_format(path: Path) -> str:
    suffix = path.suffix.lower().lstrip(".")
    if suffix == "md":
        return "markdown"
    if suffix == "py":
        return "python"
    return suffix or "binary"


def slugify(value: str) -> str:
    slug = value.casefold().strip()
    slug = re.sub(r"[^\w가-힣]+", "-", slug, flags=re.UNICODE)
    return slug.strip("-") or "uncategorized"


def require_unique(records: list[dict], key: str, label: str) -> None:
    values = [record.get(key) for record in records]
    duplicates = sorted(value for value, count in Counter(values).items() if count > 1)
    if duplicates:
        raise VaultError(f"duplicate {label}: {duplicates}")


def clean_generated_tree(path: Path) -> None:
    if not path.exists():
        path.mkdir(parents=True)
        return
    regular_files = [p for p in path.rglob("*") if p.is_file() and not p.is_symlink()]
    if regular_files:
        names = ", ".join(str(p.relative_to(VAULT)) for p in regular_files)
        raise VaultError(f"refusing to replace regular files in generated tree: {names}")
    for item in sorted(path.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if item.is_symlink():
            item.unlink()
        elif item.is_dir():
            item.rmdir()


def ensure_link(link: Path, target: Path) -> None:
    link.parent.mkdir(parents=True, exist_ok=True)
    if link.exists() or link.is_symlink():
        if not link.is_symlink():
            raise VaultError(f"refusing to overwrite regular file {link.relative_to(VAULT)}")
        link.unlink()
    relative = os.path.relpath(target, start=link.parent)
    link.symlink_to(relative)


def validate_frontmatter(node: dict, path: Path) -> None:
    if path.suffix != ".md":
        raise VaultError(f"semantic node must be Markdown: {node['id']} -> {path}")
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise VaultError(f"missing YAML frontmatter: {path.relative_to(VAULT)}")
    header = text.split("---\n", 2)[1]
    id_match = re.search(r"^id:\s*[\"']?([^\"'\n]+)[\"']?\s*$", header, re.MULTILINE)
    type_match = re.search(r"^type:\s*[\"']?([^\"'\n]+)[\"']?\s*$", header, re.MULTILINE)
    if not id_match or id_match.group(1).strip() != node["id"]:
        raise VaultError(f"frontmatter id mismatch: {path.relative_to(VAULT)}")
    if not type_match or type_match.group(1).strip() != node["type"]:
        raise VaultError(f"frontmatter type mismatch: {path.relative_to(VAULT)}")


def validate_wikilinks(nodes: list[dict]) -> None:
    stems = {Path(node["file"]).stem for node in nodes}
    missing: list[str] = []
    pattern = re.compile(r"\[\[([^]|#]+)(?:#[^]|]+)?(?:\|[^]]+)?\]\]")
    for node in nodes:
        path = VAULT / node["file"]
        text = path.read_text(encoding="utf-8")
        for target in pattern.findall(text):
            target = target.strip()
            if target not in stems:
                missing.append(f"{node['id']} -> {target}")
    if missing:
        raise VaultError("unresolved wikilinks: " + "; ".join(sorted(missing)))


def validate_nodes(nodes: list[dict], node_types: dict) -> dict[str, dict]:
    require_unique(nodes, "id", "node id")
    require_unique(nodes, "file", "node file")
    known_types = node_types["node_types"]
    index: dict[str, dict] = {}
    for node in nodes:
        missing = [
            field
            for field in ("id", "type", "title", "status", "file", "summary", "keywords", "project", "topics")
            if field not in node
        ]
        if missing:
            raise VaultError(f"node {node.get('id')} missing fields: {missing}")
        if node["type"] not in known_types:
            raise VaultError(f"unknown node type {node['type']} for {node['id']}")
        if node["status"] not in known_types[node["type"]]["allowed_statuses"]:
            raise VaultError(f"invalid status {node['status']} for {node['id']}")
        path = (VAULT / node["file"]).resolve()
        try:
            path.relative_to(FILES.resolve())
        except ValueError as exc:
            raise VaultError(f"node path escapes files/: {node['file']}") from exc
        if not path.is_file():
            raise VaultError(f"missing node file: {node['file']}")
        validate_frontmatter(node, path)
        if len(node["keywords"]) != len(set(node["keywords"])):
            raise VaultError(f"duplicate keywords in {node['id']}")
        index[node["id"]] = node
    validate_wikilinks(nodes)
    return index


def validate_edges(edges: list[dict], nodes: dict[str, dict], relation_types: dict) -> None:
    require_unique(edges, "id", "edge id")
    known = relation_types["relations"]
    triples: set[tuple[str, str, str]] = set()
    required_fields = {"id", "from", "relation", "to", "confidence", "evidence", "rationale"}
    allowed_fields = required_fields | {"proposed_by", "review_status"}
    for edge in edges:
        missing = sorted(required_fields - set(edge))
        if missing:
            raise VaultError(f"edge {edge.get('id')} missing fields: {missing}")
        extras = sorted(set(edge) - allowed_fields)
        if extras:
            raise VaultError(f"edge {edge.get('id')} has unsupported fields: {extras}")
        if edge["from"] not in nodes or edge["to"] not in nodes:
            raise VaultError(f"edge endpoint missing: {edge['id']}")
        if edge["relation"] not in known:
            raise VaultError(f"unknown relation {edge['relation']} in {edge['id']}")
        spec = known[edge["relation"]]
        source_type = nodes[edge["from"]]["type"]
        target_type = nodes[edge["to"]]["type"]
        if source_type not in spec["domain"]:
            raise VaultError(f"domain violation {edge['id']}: {source_type} {edge['relation']}")
        if target_type not in spec["range"]:
            raise VaultError(f"range violation {edge['id']}: {edge['relation']} {target_type}")
        if edge["confidence"] not in {"high", "medium", "low"}:
            raise VaultError(f"invalid confidence in {edge['id']}")
        if not edge["evidence"]:
            raise VaultError(f"edge lacks evidence: {edge['id']}")
        if edge.get("review_status", "accepted") not in {"accepted", "rejected", "provisional"}:
            raise VaultError(f"invalid review_status in {edge['id']}")
        if not isinstance(edge.get("proposed_by", []), list):
            raise VaultError(f"proposed_by must be a list in {edge['id']}")
        triple = (edge["from"], edge["relation"], edge["to"])
        if triple in triples:
            raise VaultError(f"duplicate edge triple: {triple}")
        triples.add(triple)
    for relation in ("is_a", "part_of", "depends_on", "precedes", "generalizes", "refines", "supersedes"):
        validate_acyclic_relation(edges, relation)


def validate_acyclic_relation(edges: list[dict], relation: str) -> None:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        if edge["relation"] == relation:
            if edge["from"] == edge["to"]:
                raise VaultError(f"self edge forbidden for {relation}: {edge['id']}")
            adjacency[edge["from"]].add(edge["to"])
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str, trail: list[str]) -> None:
        if node_id in visiting:
            cycle = " -> ".join(trail + [node_id])
            raise VaultError(f"cycle in {relation}: {cycle}")
        if node_id in visited:
            return
        visiting.add(node_id)
        for target in sorted(adjacency[node_id]):
            visit(target, trail + [node_id])
        visiting.remove(node_id)
        visited.add(node_id)

    for source in sorted(adjacency):
        visit(source, [])


def write_node_csv(nodes: list[dict]) -> None:
    with NODES_CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["id", "type", "title", "status", "file", "project", "topics", "keywords", "summary"],
        )
        writer.writeheader()
        for node in sorted(nodes, key=lambda item: item["id"]):
            writer.writerow(
                {
                    "id": node["id"],
                    "type": node["type"],
                    "title": node["title"],
                    "status": node["status"],
                    "file": node["file"],
                    "project": node["project"],
                    "topics": "|".join(node["topics"]),
                    "keywords": "|".join(node["keywords"]),
                    "summary": node["summary"],
                }
            )


def write_edge_csv(edges: list[dict]) -> None:
    with EDGES_CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["id", "from", "relation", "to", "confidence", "review_status", "proposed_by", "evidence", "rationale"],
        )
        writer.writeheader()
        for edge in sorted(edges, key=lambda item: item["id"]):
            writer.writerow(
                {
                    "id": edge["id"],
                    "from": edge["from"],
                    "relation": edge["relation"],
                    "to": edge["to"],
                    "confidence": edge["confidence"],
                    "review_status": edge.get("review_status", "accepted"),
                    "proposed_by": "|".join(edge.get("proposed_by", [])),
                    "evidence": "|".join(edge["evidence"]),
                    "rationale": edge["rationale"],
                }
            )


def write_keyword_indexes(nodes: list[dict], edges: list[dict]) -> None:
    keyword_nodes: dict[str, set[str]] = defaultdict(set)
    display: dict[str, str] = {}
    for node in nodes:
        for keyword in node["keywords"]:
            normalized = keyword.casefold().strip()
            keyword_nodes[normalized].add(node["id"])
            display.setdefault(normalized, keyword)
    keyword_records = [
        {
            "keyword": display[key],
            "normalized_keyword": key,
            "count": len(keyword_nodes[key]),
            "node_ids": sorted(keyword_nodes[key]),
        }
        for key in sorted(keyword_nodes)
    ]
    dump_jsonl(KEYWORD_INDEX_PATH, keyword_records)

    pair_weights: Counter[tuple[str, str]] = Counter()
    for node in nodes:
        keys = sorted({keyword.casefold().strip() for keyword in node["keywords"]})
        for left, right in combinations(keys, 2):
            pair_weights[(left, right)] += 1
    explicit_pairs = Counter()
    node_keywords = {
        node["id"]: {keyword.casefold().strip() for keyword in node["keywords"]} for node in nodes
    }
    for edge in edges:
        for left in node_keywords[edge["from"]]:
            for right in node_keywords[edge["to"]]:
                if left == right:
                    continue
                explicit_pairs[tuple(sorted((left, right)))] += 1
    with KEYWORD_EDGES_CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["keyword_a", "keyword_b", "cooccurrence_weight", "explicit_edge_weight"],
        )
        writer.writeheader()
        for pair in sorted(set(pair_weights) | set(explicit_pairs)):
            writer.writerow(
                {
                    "keyword_a": display[pair[0]],
                    "keyword_b": display[pair[1]],
                    "cooccurrence_weight": pair_weights[pair],
                    "explicit_edge_weight": explicit_pairs[pair],
                }
            )


def note_link(node: dict) -> str:
    return f"[[{Path(node['file']).stem}|{node['title']}]]"


def write_backlink_index(nodes: list[dict], edges: list[dict]) -> None:
    index = {node["id"]: node for node in nodes}
    incoming: dict[str, list[dict]] = defaultdict(list)
    outgoing: dict[str, list[dict]] = defaultdict(list)
    for edge in edges:
        outgoing[edge["from"]].append(edge)
        incoming[edge["to"]].append(edge)
    lines = [
        "---",
        "id: generated-backlink-index",
        "type: map_of_content",
        "generated: true",
        "---",
        "",
        "# Backlink Index",
        "",
        "이 파일은 `build_vault.py`가 typed edge 원장에서 생성한 읽기 전용 탐색 view다.",
        "",
    ]
    for node in sorted(nodes, key=lambda item: (item["type"], item["title"])):
        lines.extend([f"## {note_link(node)}", ""])
        if outgoing[node["id"]]:
            lines.append("Outbound:")
            lines.append("")
            for edge in sorted(outgoing[node["id"]], key=lambda item: (item["relation"], item["to"])):
                lines.append(f"- `{edge['relation']}` → {note_link(index[edge['to']])} (`{edge['id']}`)")
            lines.append("")
        if incoming[node["id"]]:
            lines.append("Inbound:")
            lines.append("")
            for edge in sorted(incoming[node["id"]], key=lambda item: (item["relation"], item["from"])):
                lines.append(f"- {note_link(index[edge['from']])} → `{edge['relation']}` (`{edge['id']}`)")
            lines.append("")
        if not outgoing[node["id"]] and not incoming[node["id"]]:
            lines.extend(["- 연결된 typed edge 없음", ""])
    BACKLINK_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_manifest(nodes: list[dict], artifacts: list[dict]) -> None:
    records: list[dict] = []
    for node in nodes:
        path = VAULT / node["file"]
        records.append(
            {
                "id": node["id"],
                "record_kind": "semantic_node",
                "node_type": node["type"],
                "title": node["title"],
                "status": node["status"],
                "file": node["file"],
                "format": canonical_format(path),
                "sha256": sha256(path),
                "summary": node["summary"],
                "keywords": node["keywords"],
                "source_scope": node.get("source_scope", []),
                "generated": False,
            }
        )
    for artifact in artifacts:
        path = VAULT / artifact["file"]
        if not path.is_file():
            raise VaultError(f"missing artifact file: {artifact['file']}")
        records.append(
            {
                "id": artifact["id"],
                "record_kind": "artifact",
                "node_type": None,
                "title": artifact.get("title"),
                "status": None,
                "file": artifact["file"],
                "format": canonical_format(path),
                "sha256": sha256(path),
                "summary": artifact["summary"],
                "keywords": artifact["keywords"],
                "source_scope": artifact.get("source_scope", []),
                "generated": artifact.get("generated", False),
            }
        )
    require_unique(records, "id", "manifest id")
    require_unique(records, "file", "manifest file")
    dump_jsonl(MANIFEST_PATH, sorted(records, key=lambda item: item["id"]))


def build_views(nodes: list[dict]) -> None:
    clean_generated_tree(VAULT / "views")
    for node in nodes:
        target = VAULT / node["file"]
        name = Path(node["file"]).name
        destinations = [
            VAULT / "views" / "by-node-type" / node["type"] / name,
            VAULT / "views" / "by-project" / node["project"] / name,
            VAULT / "views" / "by-status" / node["status"] / name,
        ]
        destinations.extend(VAULT / "views" / "by-topic" / topic / name for topic in node["topics"])
        if node["type"] == "map_of_content":
            destinations.append(VAULT / "views" / "maps-of-content" / name)
        for destination in destinations:
            ensure_link(destination, target)


def build_convenience_links() -> None:
    links = {
        VAULT / "README.md": FILES / "markdown" / "vault-readme.md",
        VAULT / "graph" / "edges.jsonl": EDGES_PATH,
        VAULT / "graph" / "keyword-index.jsonl": KEYWORD_INDEX_PATH,
        VAULT / "graph" / "keyword-edges.csv": KEYWORD_EDGES_CSV_PATH,
        VAULT / "graph" / "backlink-index.md": BACKLINK_PATH,
        VAULT / "manifests" / "files.jsonl": MANIFEST_PATH,
        VAULT / "schemas" / "node-types.json": NODE_TYPES_PATH,
        VAULT / "schemas" / "relation-types.json": RELATION_TYPES_PATH,
        VAULT / "schemas" / "manifest.schema.json": FILES / "json" / "manifest.schema.json",
        VAULT / "schemas" / "edge.schema.json": FILES / "json" / "edge.schema.json",
        VAULT / "scripts" / "build-vault.py": Path(__file__).resolve(),
    }
    for link, target in links.items():
        ensure_link(link, target)


def validate_symlinks() -> None:
    root = VAULT.resolve()
    failures: list[str] = []
    for link in [p for p in VAULT.rglob("*") if p.is_symlink()]:
        if not link.exists():
            failures.append(f"broken: {link.relative_to(VAULT)}")
            continue
        try:
            link.resolve().relative_to(root)
        except ValueError:
            failures.append(f"escapes vault: {link.relative_to(VAULT)}")
    if failures:
        raise VaultError("invalid symlinks: " + "; ".join(failures))


def validate_canonical_files(nodes: list[dict], artifacts: list[dict]) -> None:
    registered = {node["file"] for node in nodes} | {artifact["file"] for artifact in artifacts}
    internal_generated = {
        str(MANIFEST_PATH.relative_to(VAULT)),
        str(REPORT_PATH.relative_to(VAULT)),
    }
    expected_dirs = {
        ".md": "markdown",
        ".json": "json",
        ".jsonl": "jsonl",
        ".csv": "csv",
        ".py": "python",
        ".txt": "text",
    }
    unregistered: list[str] = []
    for path in sorted(FILES.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = str(path.relative_to(VAULT))
        if relative not in registered and relative not in internal_generated:
            unregistered.append(relative)
        expected = expected_dirs.get(path.suffix.lower())
        if expected and path.parent.name != expected:
            raise VaultError(f"format directory mismatch: {relative} should be under files/{expected}/")
        if path.suffix == ".json":
            load_json(path)
        elif path.suffix == ".jsonl":
            load_jsonl(path)
        elif path.suffix == ".csv":
            with path.open("r", encoding="utf-8", newline="") as handle:
                if not next(csv.reader(handle), None):
                    raise VaultError(f"empty CSV: {relative}")
        elif path.suffix == ".py":
            compile(path.read_text(encoding="utf-8"), relative, "exec")
        else:
            path.read_text(encoding="utf-8")
    if unregistered:
        raise VaultError("unregistered canonical files: " + ", ".join(unregistered))

    manifest = load_jsonl(MANIFEST_PATH)
    if len(manifest) != len(nodes) + len(artifacts):
        raise VaultError("manifest record count does not match node + artifact registries")
    require_unique(manifest, "id", "manifest id")
    require_unique(manifest, "file", "manifest file")
    required_fields = {"id", "record_kind", "file", "format", "sha256", "summary", "keywords"}
    allowed_fields = required_fields | {
        "node_type",
        "title",
        "status",
        "source_scope",
        "generated",
    }
    for record in manifest:
        missing = sorted(required_fields - set(record))
        extras = sorted(set(record) - allowed_fields)
        if missing:
            raise VaultError(f"manifest record {record.get('id')} missing fields: {missing}")
        if extras:
            raise VaultError(f"manifest record {record.get('id')} has unsupported fields: {extras}")
        if record["record_kind"] not in {"semantic_node", "artifact"}:
            raise VaultError(f"invalid manifest record_kind: {record['id']}")
        if not re.fullmatch(r"[a-f0-9]{64}", record["sha256"]):
            raise VaultError(f"invalid manifest sha256: {record['id']}")
        path = VAULT / record["file"]
        if record["sha256"] != sha256(path):
            raise VaultError(f"manifest hash mismatch: {record['file']}")


def build() -> tuple[int, int, int]:
    node_types = load_json(NODE_TYPES_PATH)
    relation_types = load_json(RELATION_TYPES_PATH)
    artifact_doc = load_json(ARTIFACTS_PATH)
    nodes = discover_nodes()
    artifacts = artifact_doc["artifacts"]
    edges = load_jsonl(EDGES_PATH)
    node_index = validate_nodes(nodes, node_types)
    validate_edges(edges, node_index, relation_types)
    write_node_csv(nodes)
    write_edge_csv(edges)
    write_keyword_indexes(nodes, edges)
    write_backlink_index(nodes, edges)
    build_views(nodes)
    build_convenience_links()
    write_manifest(nodes, artifacts)
    validate_symlinks()
    validate_canonical_files(nodes, artifacts)
    regular_outside_files = [
        path
        for path in VAULT.rglob("*")
        if path.is_file() and not path.is_symlink() and FILES.resolve() not in path.resolve().parents
    ]
    if regular_outside_files:
        raise VaultError(
            "regular files outside canonical files/: "
            + ", ".join(str(path.relative_to(VAULT)) for path in regular_outside_files)
        )
    return len(nodes), len(edges), len(artifacts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Build derived views and report validation.")
    parser.parse_args()
    try:
        node_count, edge_count, artifact_count = build()
    except VaultError as exc:
        message = f"FAIL\n{exc}\n"
        REPORT_PATH.write_text(message, encoding="utf-8")
        print(message, end="", file=sys.stderr)
        return 1
    message = (
        "PASS\n"
        f"semantic_nodes={node_count}\n"
        f"typed_edges={edge_count}\n"
        f"registered_artifacts={artifact_count}\n"
        "json=valid\n"
        "wikilinks=resolved\n"
        "symlinks=resolved_and_internal\n"
        "relation_domain_range=valid\n"
        "relation_cycles=absent\n"
        "duplicate_edge_triples=absent\n"
        "manifest_hashes=valid\n"
        "canonical_storage=files_only\n"
    )
    REPORT_PATH.write_text(message, encoding="utf-8")
    print(message, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
