import sys, json
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Hello from FarsiScript!")

def start(port=8080):
    server = HTTPServer(("localhost", port), Handler)
    print(f"Server running on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    start(int(sys.argv[1]) if len(sys.argv)>1 else 8080)
