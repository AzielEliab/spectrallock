"""Local SpectralLock UI. Bind 127.0.0.1 only.

Rosetta spectral analysis: SpectralLock lenses, overlays, ink/page targets.
Same family as Aziel Corpus Library OCR. Dark gold. No CDN. No telemetry.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from urllib.parse import parse_qs, urlparse

from spectrallock import LIMITATION, __version__
from spectrallock.debug import debug
from spectrallock.engine import (
    PLAIN_NOT_IMAGE,
    analyze,
    list_lenses,
    list_modes,
    list_targets,
    load_rgb_bytes,
    make_receipt,
    normalize_lenses,
    normalize_target,
    png_bytes,
    sha256_hex,
    synthetic_page,
)

LOOPBACK = frozenset({"127.0.0.1", "localhost", "::1"})
WEB = files("spectrallock") / "web"
MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
}
MAX_UPLOAD = 12 * 1024 * 1024
TOO_BIG = "That picture is too big (max 12 MB)."
NO_PICTURE = "No picture in the upload."


def _web_bytes(name: str) -> bytes:
    return (WEB / name).read_bytes()


class Handler(BaseHTTPRequestHandler):
    server_version = f"SpectralLock/{__version__}"

    def log_message(self, fmt: str, *args: object) -> None:
        return

    def _send(self, status: int, body: bytes, content_type: str, extra: dict[str, str] | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if extra:
            for key, value in extra.items():
                self.send_header(key, value)
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
        if path in {"/api/modes", "/api/lenses"}:
            self._json(200, {
                "modes": list_modes(),
                "lenses": list_lenses(),
                "targets": list_targets(),
                "advisory": LIMITATION,
                "version": __version__,
                "author": "Aziel Eliab",
                "rosetta_spectral_analysis": True,
                "corpus_ocr_aligned": True,
                "simple_default": True,
            })
            return
        if path == "/api/targets":
            self._json(200, {
                "targets": list_targets(),
                "advisory": LIMITATION,
                "version": __version__,
            })
            return
        if path in {"/api/sample", "/api/synthetic_page"}:
            png = png_bytes(synthetic_page(192, 192))
            debug(f"sample png_bytes={len(png)}")
            extra = {
                "Content-Disposition": 'inline; filename="synthetic_page.png"',
                "X-SpectralLock-Sample": "synthetic_page",
            }
            self._send(200, png, "image/png", extra)
            return
        if path == "/api/doctor":
            self._json(200, {
                "product": "spectrallock",
                "version": __version__,
                "loopback": True,
                "telemetry": False,
                "modes": list(m["id"] for m in list_modes()),
                "lenses": list(m["id"] for m in list_lenses()),
                "targets": list(t["id"] for t in list_targets()),
                "rosetta_spectral_analysis": True,
                "corpus_ocr_aligned": True,
                "advisory": LIMITATION,
            })
            return
        self._json(404, {"error": "not found", "advisory": LIMITATION})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path != "/api/overlay":
            self._json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length") or "0")
        except ValueError:
            self._json(400, {"error": NO_PICTURE, "advisory": LIMITATION})
            return
        if length <= 0:
            self._json(400, {"error": NO_PICTURE, "advisory": LIMITATION})
            return
        if length > MAX_UPLOAD:
            debug(f"upload rejected length={length} max={MAX_UPLOAD}")
            self._json(400, {"error": TOO_BIG, "advisory": LIMITATION})
            return
        raw = self.rfile.read(length)
        ctype = (self.headers.get("Content-Type") or "").lower()
        mode = "rosetta"
        target = "ink"
        lens_values: list[str] = []
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
            mode = str(payload.get("mode") or payload.get("lens") or "rosetta")
            target = str(payload.get("target") or payload.get("polarity") or "ink")
            extra_lenses = payload.get("lenses") or payload.get("lens")
            if extra_lenses:
                if isinstance(extra_lenses, (list, tuple)):
                    lens_values.extend(str(x) for x in extra_lenses)
                else:
                    lens_values.append(str(extra_lenses))
            import base64

            b64 = payload.get("b64") or payload.get("image") or ""
            try:
                img_bytes = base64.b64decode(b64)
            except Exception:
                self._json(400, {"error": PLAIN_NOT_IMAGE, "advisory": LIMITATION})
                return
            if not img_bytes:
                self._json(400, {"error": NO_PICTURE, "advisory": LIMITATION})
                return
            as_json = True
        elif "multipart/form-data" in ctype:
            mode, img_bytes, target, lens_values = _parse_multipart(raw, self.headers.get("Content-Type") or "")
            if not img_bytes:
                self._json(400, {"error": NO_PICTURE, "advisory": LIMITATION})
                return
        else:
            qs = parse_qs(urlparse(self.path).query)
            if "mode" in qs:
                mode = qs["mode"][0]
            if "lens" in qs:
                lens_values.extend(qs["lens"])
            if "target" in qs:
                target = qs["target"][0]
        try:
            rgb = load_rgb_bytes(img_bytes)
        except ValueError as exc:
            debug("overlay decode ValueError")
            self._json(400, {"error": str(exc), "advisory": LIMITATION})
            return
        except Exception:  # noqa: BLE001
            debug("overlay decode failed")
            self._json(400, {"error": PLAIN_NOT_IMAGE, "advisory": LIMITATION})
            return
        try:
            selected = normalize_lenses(
                mode=None if lens_values else mode,
                lenses=lens_values or None,
            )
            dest = normalize_target(target)
            result = analyze(rgb, lenses=selected, target=dest)
        except ValueError as exc:
            self._json(400, {"error": str(exc), "advisory": LIMITATION})
            return
        png = png_bytes(result.rgb)
        rec = make_receipt(
            mode=result.mode,
            paper=result.paper,
            sha256_in=sha256_hex(img_bytes),
            sha256_out=sha256_hex(png),
            size_in=len(img_bytes),
            size_out=len(png),
            width=result.width,
            height=result.height,
            target=result.target,
            lenses=result.lenses,
        )
        debug(
            f"ui overlay mode={rec['mode']} target={rec['target']} paper={rec['paper']} "
            f"size_in={rec['size_in']} size_out={rec['size_out']} "
            f"sha256_in={rec['sha256_in']} sha256_out={rec['sha256_out']}"
        )
        extra = {
            "X-SpectralLock-Mode": rec["mode"],
            "X-SpectralLock-Lenses": ",".join(rec.get("lenses") or [rec["mode"]]),
            "X-SpectralLock-Target": rec["target"],
            "X-SpectralLock-Paper": rec["paper"],
            "X-SpectralLock-Sha256-In": rec["sha256_in"],
            "X-SpectralLock-Sha256-Out": rec["sha256_out"],
            "X-SpectralLock-Size-In": str(rec["size_in"]),
            "X-SpectralLock-Size-Out": str(rec["size_out"]),
        }
        if as_json:
            import base64

            meta = result.to_meta()
            meta.update(rec)
            meta["png_b64"] = base64.b64encode(png).decode("ascii")
            self._json(200, meta)
            return
        self._send(200, png, "image/png", extra)


def _parse_multipart(raw: bytes, content_type: str) -> tuple[str, bytes, str, list[str]]:
    """Minimal multipart parser: mode/lens/target fields + file field."""
    mode = "rosetta"
    target = "ink"
    lenses: list[str] = []
    img = b""
    bound = b""
    for part in content_type.split(";"):
        part = part.strip()
        if part.lower().startswith("boundary="):
            bound = part.split("=", 1)[1].strip().strip('"').encode("utf-8")
    if not bound:
        return mode, raw, target, lenses
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
        value = body.decode("utf-8", "replace").strip()
        if "name=\"mode\"" in header:
            mode = value
        elif "name=\"lens\"" in header or "name=\"lenses\"" in header:
            if value:
                lenses.append(value)
        elif "name=\"target\"" in header or "name=\"polarity\"" in header:
            target = value
        elif "name=\"file\"" in header or "name=\"image\"" in header or "filename=" in header:
            img = body
    return mode, img, target, lenses


def make_server(host: str = "127.0.0.1", port: int = 8861) -> ThreadingHTTPServer:
    if host not in LOOPBACK:
        raise ValueError("SpectralLock UI binds loopback only (127.0.0.1)")
    debug(f"make_server host={host} port={port}")
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
