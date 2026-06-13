import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from models.loader import models_loaded
from config import HEALTH_PORT

logger = logging.getLogger(__name__)


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/health":
            try:
                status = models_loaded()
                all_ok = all(status.values())
                body = json.dumps(
                    {
                        "status": "ok" if all_ok else "degraded",
                        **status,
                    }
                ).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.send_header("X-Content-Type-Options", "nosniff")
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                logger.error(f"Health check error: {e}")
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format: str, *args) -> None:
        pass


def run_health_server() -> None:
    server = HTTPServer(("0.0.0.0", HEALTH_PORT), HealthHandler)
    logger.info(f"Health server running on port {HEALTH_PORT}")
    try:
        server.serve_forever()
    except Exception as e:
        logger.error(f"Health server crashed: {e}")
        raise
