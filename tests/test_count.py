"""GET /count must return {project, views, downloads, total}."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / "workers" / "download-tracker" / "src" / "index.js"

COUNT_KEYS = ("project", "views", "downloads", "total")


def _worker_js() -> str:
    return WORKER.read_text(encoding="utf-8")


def _count_handler(js: str) -> str:
    start = js.find('url.pathname === "/count"')
    assert start != -1, "GET /count handler missing from download-tracker Worker"
    end = js.find("if (url.pathname === \"/stats\"", start)
    assert end != -1, "GET /count handler is not followed by /stats"
    return js[start:end]


def test_count_endpoint_returns_project_views_downloads_total() -> None:
    js = _worker_js()
    handler = _count_handler(js)
    assert "countPayload" in handler
    assert "function countPayload(" in js
    assert "return { project: PROJECT, views, downloads, total };" in js
    assert "return json({ project: PROJECT, total: stats.total || 0 });" not in js


def test_count_payload_executes_four_fields() -> None:
    node = shutil.which("node")
    assert node, "node is required to execute Worker countPayload"
    js = _worker_js()
    start = js.find("function countPayload(")
    end = js.find("function viewsKey(", start)
    assert start != -1 and end != -1
    fn = js[start:end]
    script = (
        'const PROJECT = "spectrallock";\n'
        f"{fn}\n"
        "const out = countPayload({ views: 32, downloads: 49, total: 49 });\n"
        "process.stdout.write(JSON.stringify(out));\n"
    )
    raw = subprocess.check_output([node, "--input-type=module", "-e", script], text=True)
    body = json.loads(raw)
    assert list(body.keys()) == list(COUNT_KEYS)
    assert body == {"project": "spectrallock", "views": 32, "downloads": 49, "total": 49}


def test_count_payload_keys_and_openapi_contract() -> None:
    js = _worker_js()
    for key in COUNT_KEYS:
        assert key in js
    assert '"/count"' in js
    assert 'required: ["project", "views", "downloads", "total"]' in js
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "{project, views, downloads, total}" in readme
    worker_readme = (ROOT / "workers" / "download-tracker" / "README.md").read_text(encoding="utf-8")
    assert "{project, views, downloads, total}" in worker_readme
