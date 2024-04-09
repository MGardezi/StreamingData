import socket

def is_port_available(port):
    try:
        # Try to create a socket with the given port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("localhost", port))
        return True
    except OSError:
        # Port is not available
        return False

# Example usage
port = 8501  # Port to check
if is_port_available(port):
    print(f"Port {port} is available")
else:
    print(f"Port {port} is not available")
