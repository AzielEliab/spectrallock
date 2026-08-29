"""Local SpectralLock UI. Bind 127.0.0.1 only.

Drop/upload a photograph, pick a mode, see before/after. Advisory overlay.
Not forensic proof. Dark gold. No CDN.
"""

from __future__ import annotations

import io
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from urllib.parse import urlparse

from PIL import Image

from spectrallock.engine import LIMITATION, apply_mode, list_modes, save_rgb

LOOPBACK = frozenset({"127.0.0.1", "localhost", "::1"})
WEB = files("spectrallock") / "web"
MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
}
MAX_UPLOAD = 12 * 1024 * 1024


def _web_bytes(name: str) -> bytes:
    return (WEB / name).read_bytes()


def _read_image_bytes(raw: bytes) -> "object":
    img = Image.open(io.BytesIO(raw))
    if img.mode != "RGB":
        img = img.convert("RGB")
    import numpy as np

    return np.asarray(img, dtype=np.float32) / 255.0


class Handler(BaseHTTPRequestHandler):
    server_version = "SpectralLock/0.1.0"

    def log_message(self, fmt: str, *args: object) -> None:
        return

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, obj: object) -> None:
        body = json.dumps(obj, indent=2, ensure_ascii=False).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in {"/", "/index.html"}:
            self._send(200, _web_bytes("index.html"), MIME[".html"])
            return
        if path == "/style.css":
            self._send(200, _web_bytes("style.css"), MIME[".css"])
            return
        if path == "/app.js":
            self._send(200, _web_bytes("app.js"), MIME[".js"])
            return
        if path == "/api/modes":
            self._json(200, {"modes": list_modes(), "advisory": LIMITATION})
            return
        self._json(404, {"error": "not found", "advisory": LIMITATION})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path != "/api/overlay":
            self._json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length") or "0")
        if length <= 0 or length > MAX_UPLOAD:
            self._json(400, {"error": "image too large or empty", "advisory": LIMITATION})
            return
        raw = self.rfile.read(length)
        ctype = (self.headers.get("Content-Type") or "").lower()
        mode = "rosetta"
        img_bytes = raw
        as_json = False
        if "application/json" in ctype:
            try:
                payload = json.loads(raw.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                self._json(400, {"error": "JSON body required"})
                return
            if not isinstance(payload, dict):
                self._json(400, {"error": "JSON object required"})
                return
            mode = str(payload.get("mode") or "rosetta")
            import base64

            b64 = payload.get("b64") or payload.get("image") or ""
            try:
                img_bytes = base64.b64decode(b64)
            except Exception:
                self._json(400, {"error": "b64 image required"})
                return
            as_json = True
        elif "multipart/form-data" in ctype:
            mode, img_bytes = _parse_multipart(raw, self.headers.get("Content-Type") or "")
        # else: raw image body; mode from query
        else:
            from urllib.parse import parse_qs

            qs = parse_qs(urlparse(self.path).query)
            if "mode" in qs:
                mode = qs["mode"][0]
        try:
            rgb = _read_image_bytes(img_bytes)
        except Exception as exc:  # noqa: BLE001
            self._json(400, {"error": f"could not decode image: {exc}", "advisory": LIMITATION})
            return
        try:
            result = apply_mode(rgb, mode)
        except ValueError as exc:
            self._json(400, {"error": str(exc), "advisory": LIMITATION})
            return
        buf = io.BytesIO()
        # reuse save via PIL
        from PIL import Image as PILImage
        import numpy as np

        arr = np.clip(np.round(result.rgb * 255.0), 0, 255).astype(np.uint8)
        PILImage.fromarray(arr, "RGB").save(buf, format="PNG")
        png = buf.getvalue()
        if as_json:
            import base64

            meta = result.to_meta()
            meta["png_b64"] = base64.b64encode(png).decode("ascii")
            self._json(200, meta)
            return
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.send_header("Content-Length", str(len(png)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-SpectralLock-Mode", result.mode)
        self.send_header("X-SpectralLock-Paper", result.paper)
        self.end_headers()
        self.wfile.write(png)


def _parse_multipart(raw: bytes, content_type: str) -> tuple[str, bytes]:
    """Minimal multipart parser: mode field + file field."""
    mode = "rosetta"
    img = b""
    bound = b""
    for part in content_type.split(";"):
        part = part.strip()
        if part.lower().startswith("boundary="):
            bound = part.split("=", 1)[1].strip().strip('"').encode("utf-8")
    if not bound:
        return mode, raw
    marker = b"--" + bound
    for chunk in raw.split(marker):
        chunk = chunk.strip(b"\r\n")
        if not chunk or chunk == b"--":
            continue
        if b"\r\n\r\n" not in chunk:
            continue
        head, body = chunk.split(b"\r\n\r\n", 1)
        if body.endswith(b"\r\n"):
            body = body[:-2]
        header = head.decode("utf-8", "replace").lower()
        if "name=\"mode\"" in header:
            mode = body.decode("utf-8", "replace").strip()
        elif "name=\"file\"" in header or "name=\"image\"" in header or "filename=" in header:
            img = body
    return mode, img


def make_server(host: str = "127.0.0.1", port: int = 8861) -> ThreadingHTTPServer:
    if host not in LOOPBACK:
        raise ValueError("SpectralLock UI binds loopback only (127.0.0.1)")
    return ThreadingHTTPServer((host, port), Handler)


def serve(host: str = "127.0.0.1", port: int = 8861) -> None:
    httpd = make_server(host, port)
    bound_host, bound_port = httpd.server_address[:2]
    print(f"SpectralLock UI http://{bound_host}:{bound_port} (loopback only)")
    print(LIMITATION)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        httpd.server_close()
