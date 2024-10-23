from http.server import HTTPServer, BaseHTTPRequestHandler
import sys

class SecureHTTPRequestHandler(BaseHTTPRequestHandler):
    ALLOWED_CONNECTIONS = [24003, 24004]  

    def do_GET(self):
        client_ip, client_port = self.client_address
        print(client_ip, client_port)
        # Check if the client address is allowed
        if (int(client_port)) not in self.ALLOWED_CONNECTIONS:
            self.send_response(403) 
            self.end_headers()
            self.wfile.write(b'Forbidden: Access is denied.')
            return

        # If the client is allowed, send a successful response
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')

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
