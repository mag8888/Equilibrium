#!/usr/bin/env python3
"""
Простой healthcheck сервер, который не требует Django
Запускается параллельно с Gunicorn для быстрого ответа на healthcheck
"""
import http.server
import socketserver
import os
import sys

PORT = int(os.environ.get('HEALTHCHECK_PORT', '8001'))

class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health/' or self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok", "message": "Healthcheck server is running"}')
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_HEAD(self):
        if self.path == '/health/' or self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Отключаем логирование для healthcheck
        pass

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), HealthCheckHandler) as httpd:
        print(f"Healthcheck server started on port {PORT}")
        httpd.serve_forever()

