import socket

def client_program():
    host = socket.gethostname()  # Use localhost for testing on the same machine
    port = 8082  # Server socket port number
    client_port = 5000  # Specify the client port you want to use

    # Create a socket and bind it to the client port
    client_socket = socket.socket()  # Instantiate a socket object
    client_socket.bind((host, client_port))  # Bind the socket to the specified port

    client_socket.connect((host, port))  # Connect to the server

    # Create an HTTP GET request
    request_line = "GET / HTTP/1.1\r\n"  # Adjust the path as needed
    headers = f"Host: {host}:{port}\r\nConnection: close\r\n\r\n"  # Include Host header and connection close
    http_get_request = request_line + headers

    # Send the GET request
    client_socket.send(http_get_request.encode())  # Send the HTTP GET request

    # Receive the response from the server
    response = b""  # Initialize a bytes object to store the response
    while True:
        data = client_socket.recv(1024)  # Receive data in chunks
        if not data:  # If no more data, break the loop
            break
        response += data  # Append received data to the response

    print('Received from server:\n' + response.decode())  # Decode and print the server's response

    client_socket.close()  # Close the connection


if __name__ == '__main__':
    client_program()
