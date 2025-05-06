"""
Tiny zero‑dependency JSON API exposing repository content.
Start with:

>>> from pydiscovery.api_server import serve
>>> serve(repository_instance)
"""
import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from pydiscovery.repository.code_element_repository import CodeElementRepository

LOG = logging.getLogger(__name__)


class _Handler(BaseHTTPRequestHandler):
    """Dynamic handler bound to a repository instance via closure."""

    repo: CodeElementRepository  # injected later

    def _send(self, obj: Any, status: int = 200) -> None:
        body = json.dumps(obj, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # routes -----------------------------------------------------------
    def do_GET(self):  # noqa: N802
        if self.path == "/elements":
            elems = [e.to_dict() for e in self.repo.all_elements()]
            self._send(elems)
        elif self.path == "/relationships":
            rel = {
                e.name: sorted(e.dependencies)
                for e in self.repo.all_elements() if e.dependencies
            }
            self._send(rel)
        else:
            self._send({"error": "not found"}, status=404)

    # silence logs
    def log_message(self, fmt: str, *args):  # noqa: D401, ANN001
        LOG.debug(fmt, *args)


def serve(repo: CodeElementRepository, host: str = "127.0.0.1", port: int = 8000) -> None:
    _Handler.repo = repo  # type: ignore[attr-defined]
    httpd = HTTPServer((host, port), _Handler)
    LOG.info("API server running at http://%s:%d", host, port)
    httpd.serve_forever()