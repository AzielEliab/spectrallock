"""Loopback UI serves overlay PNG and modes."""

from __future__ import annotations

import io
import json
import threading
import urllib.error
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



def test_ui_sample_verify_html_and_reject(tmp_path) -> None:
    import hashlib

    httpd = make_server("127.0.0.1", 0)
    host, port = httpd.server_address[:2]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        with urllib.request.urlopen(f"http://{host}:{port}/") as res:
            html = res.read().decode()
        low = html.lower()
        assert "add file" in low
        assert "export" in low
        assert "verify" in low
        assert "sample page" in low
        assert "simple" in low
        assert "overlay only" in low or "overlay-only" in low
        assert "side by side" in low
        assert "127.0.0.1:8861" in html

        with urllib.request.urlopen(f"http://{host}:{port}/api/sample") as res:
            png = res.read()
            ctype = res.headers.get("Content-Type", "")
        assert png[:8] == b"\x89PNG\r\n\x1a\n"
        assert "image/png" in ctype

        src = tmp_path / "p.png"
        save_rgb(synthetic_page(24, 24), str(src))
        data = src.read_bytes()
        req = urllib.request.Request(
            f"http://{host}:{port}/api/overlay",
            data=json.dumps({
                "mode": "zero",
                "b64": __import__("base64").b64encode(data).decode("ascii"),
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as res:
            out = json.loads(res.read().decode())
        assert out["mode"] == "zero"
        assert out["paper"] == "ZSA-1.0"
        assert out["sha256_in"] == hashlib.sha256(data).hexdigest()
        assert out["sha256_out"]
        assert out["size_in"] == len(data)
        png_out = __import__("base64").b64decode(out["png_b64"])
        assert out["sha256_out"] == hashlib.sha256(png_out).hexdigest()

        bad = urllib.request.Request(
            f"http://{host}:{port}/api/overlay",
            data=b"not-an-image",
            headers={"Content-Type": "application/octet-stream"},
            method="POST",
        )
        try:
            urllib.request.urlopen(bad)
            raise AssertionError("expected HTTPError")
        except urllib.error.HTTPError as exc:
            body = json.loads(exc.read().decode())
            assert exc.code == 400
            assert "not a picture" in body["error"].lower()
    finally:
        httpd.shutdown()
        httpd.server_close()



def test_ui_rejects_too_large() -> None:
    import http.client

    from spectrallock.ui import MAX_UPLOAD

    assert MAX_UPLOAD == 12 * 1024 * 1024
    httpd = make_server("127.0.0.1", 0)
    host, port = httpd.server_address[:2]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        conn = http.client.HTTPConnection(host, port, timeout=3)
        conn.putrequest("POST", "/api/overlay")
        conn.putheader("Content-Type", "image/png")
        conn.putheader("Content-Length", str(MAX_UPLOAD + 1))
        conn.endheaders()
        resp = conn.getresponse()
        body = json.loads(resp.read().decode())
        assert resp.status == 400
        assert "too big" in body["error"].lower()
        conn.close()
    finally:
        httpd.shutdown()
        httpd.server_close()
