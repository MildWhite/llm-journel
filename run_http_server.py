#!/usr/bin/env python3
"""Simple HTTP server to trigger calendar commands"""
import http.server
import socketserver
import urllib.parse
import subprocess
import threading

PORT = 8765

def run_calendar_command(action, params):
    cmd = ["python", "C:\\Users\\Milo\\.claw\\skills\\google-calendar\\google_calendar.py", "--action", action]
    if params.get("summary"):
        cmd.extend(["--summary", params["summary"]])
    if params.get("start"):
        cmd.extend(["--start", params["start"]])
    if params.get("end"):
        cmd.extend(["--end", params["end"]])
    if params.get("description"):
        cmd.extend(["--description", params["description"]])
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/create?"):
            parsed = urllib.parse.parse_qs(self.path[8:])
            result = run_calendar_command("create", parsed)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"<html><body><h1>Event Created!</h1><pre>{result}</pre></body></html>".encode())
        elif self.path.startswith("/list"):
            result = run_calendar_command("list", {"time_min": "2026-05-10T00:00:00Z", "time_max": "2026-05-10T23:59:59Z"})
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"<html><body><h1>Events</h1><pre>{result}</pre></body></html>".encode())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<html><body><h1>Calendar HTTP Trigger</h1><p>/create?summary=Meeting&start=2026-05-11T14:00:00Z&end=2026-05-11T15:00:00Z</p><p>/list</p></body></html>")

print(f"Starting server on port {PORT}")
print(f"URLs:")
print(f"  Create: http://localhost:{PORT}/create?summary=Team+Meeting&start=2026-05-11T14:00:00Z&end=2026-05-11T15:00:00Z")
print(f"  List:   http://localhost:{PORT}/list")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()