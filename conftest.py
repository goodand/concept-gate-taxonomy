"""Root pytest configuration.

`test_server.py` imports `fastmcp` at module scope. When that optional
dependency is absent the import raises during collection, which aborts the
entire root run -- 77 unrelated tests stop running because of one missing
package. Skipping its collection keeps the rest of the suite usable in a bare
checkout.

This does not quietly drop coverage: `scripts/run_gates.py` runs
`test_server.py` as its own gate and reports it as BLOCKED, naming the missing
module, so the gap stays visible where it matters.
"""

collect_ignore = []

try:  # pragma: no cover - depends on the local environment
    import fastmcp  # noqa: F401
except ImportError:
    collect_ignore.append("test_server.py")
