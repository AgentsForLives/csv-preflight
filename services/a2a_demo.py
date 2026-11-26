"""Local A2A discovery and indicative pricing demo."""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parent
CARD = json.loads((ROOT / "agent-card.template.json").read_text(encoding="utf-8"))
CATALOG = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
SERVICES = {service["id"]: service for service in CATALOG["services"]}

class Handler(BaseHTTPRequestHandler):
    def setup(self):
        self.request.settimeout(5)
        super().setup()

    def send_json(self, status, value):
        payload = json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/.well-known/agent-card.json":
            self.send_json(200, CARD)
        else:
            self.send_json(404, {"error": "Route not found"})

    def do_POST(self):
        if self.path != "/a2a":
            self.send_json(404, {"error": "Route not found"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 8192:
                self.send_json(413, {"error": "Request must be 1–8192 bytes"})
                return
            request = json.loads(self.rfile.read(size))
        except (ValueError, TimeoutError):
            self.rpc_error(None, -32700, "Invalid JSON")
            return
        if not isinstance(request, dict) or request.get("jsonrpc") != "2.0":
            self.rpc_error(None, -32600, "Invalid request")
            return
        request_id = request.get("id")
        if not isinstance(request_id, (str, int)) or isinstance(request_id, bool):
            self.rpc_error(None, -32600, "A string or integer id is required")
            return
        if request.get("method") != "SendMessage":
            self.rpc_error(request_id, -32601, "Method not supported by this demo")
            return
        try:
            message = request["params"]["message"]
            service_id = message["parts"][0]["data"]["service_id"]
            if message["role"] != "ROLE_USER" or not message["messageId"]:
                raise ValueError
            service = SERVICES[service_id]
        except (KeyError, TypeError, IndexError, ValueError):
            self.rpc_error(request_id, -32602, "Use a user message with a catalog service_id")
            return
        data = {
            "service_id": service_id,
            "indicative_price": service["price"],
            "currency": CATALOG["currency"],
            "intake": CATALOG["contact"],
            "accepted": False,
        }
        reply = {"messageId": str(uuid4()), "role": "ROLE_AGENT", "parts": [{"data": data}]}
        self.send_json(200, {"jsonrpc": "2.0", "id": request_id, "result": {"message": reply}})

    def rpc_error(self, request_id, code, message):
        self.send_json(200, {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}})


if __name__ == "__main__":
    with HTTPServer(("127.0.0.1", 8787), Handler) as server:
        server.serve_forever()
