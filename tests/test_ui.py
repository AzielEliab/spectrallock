"""Loopback UI serves overlay PNG and modes."""

from __future__ import annotations

import io
import json
import threading
import urllib.request

from spectrallock.engine import save_rgb, synthetic_page
from spectrallock.ui import make_server


def test_ui_modes_and_overlay(tmp_path) -> None:
    httpd = make_server("127.0.0.1", 0)
    host, port = httpd.server_address[:2]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        with urllib.request.urlopen(f"http://{host}:{port}/api/modes") as res:
            payload = json.loads(res.read().decode())
        ids = [m["id"] for m in payload["modes"]]
        assert "zero" in ids and "balance" in ids and "uv" in ids
        src = tmp_path / "p.png"
        save_rgb(synthetic_page(24, 24), str(src))
        data = src.read_bytes()
        req = urllib.request.Request(
            f"http://{host}:{port}/api/overlay",
            data=json.dumps({
                "mode": "rosetta",
                "b64": __import__("base64").b64encode(data).decode("ascii"),
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as res:
            out = json.loads(res.read().decode())
        assert out["mode"] == "rosetta"
        assert out["width"] == 24
        png = __import__("base64").b64decode(out["png_b64"])
        assert png[:8] == b"\x89PNG\r\n\x1a\n"
        with urllib.request.urlopen(f"http://{host}:{port}/") as res:
            html = res.read().decode()
        assert "not a forensic proof" in html.lower() or "not forensic" in html.lower()
        assert "add file" in html.lower()
        assert "export" in html.lower()
        assert "127.0.0.1:8861" in html
    finally:
        httpd.shutdown()
        httpd.server_close()
