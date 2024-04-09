import socket

def find_available_port(start_port):
    end_port = 65535  # Maximum port number

    for port in range(start_port, end_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
            return port
        except OSError:
            pass
    return None

start_port = 8501  # Starting port number
port = find_available_port(start_port)

if port:
    print(f"Available port found: {port}")
else:
    print("No available port found.")
