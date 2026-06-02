#!/usr/bin/env python3
import http.server, subprocess, json, os

# Load configuration
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
try:
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
except Exception as e:
    print(f"Error loading config.json: {e}, using default values.")
    config = {}

HOST = config.get("host", "127.0.0.1")
PORT = config.get("port", 6543)
ENDPOINT = config.get("endpoint", "/open-drawer")
PRINTER_NAME = config.get("printer_name", "Printer_POS_80")
DRAWER_SEQUENCE = config.get("drawer_sequence", "\\x1B\\x70\\x00\\x19\\xFA")
CORS_ORIGIN = config.get("cors_origin", "*")

def get_available_printers():
    try:
        result = subprocess.run(['lpstat', '-p'], capture_output=True, text=True, check=True)
        printers = []
        for line in result.stdout.splitlines():
            words = line.split()
            for i, word in enumerate(words):
                cleaned = word.lower().strip(':')
                if cleaned in ('printer', 'impresora'):
                    if i + 1 < len(words):
                        printers.append(words[i+1].rstrip(':'))
                        break
        return printers
    except Exception:
        return []

class Handler(http.server.BaseHTTPRequestHandler):
    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', CORS_ORIGIN)
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == ENDPOINT:
            # 1. Validate if printer exists before trying to print
            available = get_available_printers()
            if PRINTER_NAME not in available:
                error_msg = f"Printer '{PRINTER_NAME}' is not configured on the system."
                self.send_response(400) # Bad Request
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    "ok": False,
                    "error": error_msg,
                    "available_printers": available
                }, ensure_ascii=False).encode('utf-8'))
                return

            try:
                command = f"printf '{DRAWER_SEQUENCE}' | lp -d {PRINTER_NAME} -o raw"
                subprocess.run(
                    ['sh', '-c', command],
                    capture_output=True,
                    text=True,
                    check=True
                )
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(b'{"ok":true}')
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr.strip() if e.stderr else str(e)
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    "ok": False,
                    "error": f"Error executing print command: {error_msg}"
                }, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    "ok": False,
                    "error": str(e)
                }, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_response(404)
            self.send_cors_headers()
            self.end_headers()

    def log_message(self, *args): pass

if __name__ == "__main__":
    print(f"Starting Coin Drawer Manager on http://{HOST}:{PORT}{ENDPOINT}")
    http.server.HTTPServer((HOST, PORT), Handler).serve_forever()