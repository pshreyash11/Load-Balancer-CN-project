from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
import os

class SecureHTTPRequestHandler(BaseHTTPRequestHandler):
    ALLOWED_CONNECTIONS = [24003, 24004]  # Allowed client ports

    def do_GET(self):
        client_ip, client_port = self.client_address
        print(f"Client: {client_ip}:{client_port}")

        # Check if the client port is allowed
        if int(client_port) not in self.ALLOWED_CONNECTIONS:
            self.send_response(403)  # Forbidden
            self.end_headers()
            self.wfile.write(b'Forbidden: Access is denied.')
            return

        # Extract the requested path
        requested_path = self.path.strip("/")
        
        if os.path.isfile(requested_path):
            # Serve the content of the file
            self.send_response(200)
            self.end_headers()
            with open(requested_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            # Handle file not found
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Error: File not found.')

def run(server_class=HTTPServer, handler_class=SecureHTTPRequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting secure HTTP server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 8080
    run(port=port)
