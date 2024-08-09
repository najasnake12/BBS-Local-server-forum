import socket
import threading
import sys

def handle_client(client_socket, addr, clients):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"Client: ({addr[0]}) {message}")
            # Broadcast the message to all other clients
            for client, _ in clients:
                if client != client_socket:
                    try:
                        client.send(f"{addr[0]}: {message}".encode('utf-8'))
                    except:
                        pass
        except ConnectionResetError:
            print('connection error')
    client_socket.close()
    # Remove client from the list
    clients.remove((client_socket, addr))

def start_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", port))
    server.listen(5)
    print(f"Server listening for connections on port {port}")

    # Generate and display key
    server_ip = socket.gethostbyname(socket.gethostname())
    key = f"{server_ip}:{port}"
    print(f"Share this key with clients: {key}")

    clients = []

    def accept_connections():
        while True:
            client_socket, addr = server.accept()
            print(f"Connection from {addr[0]}")
            clients.append((client_socket, addr))
            client_handler = threading.Thread(target=handle_client, args=(client_socket, addr, clients))
            client_handler.start()

    def send_messages():
        server_ip = socket.gethostbyname(socket.gethostname())
        while True:
            message = input("Enter message: ")
            if message.lower() == 'exit':
                break
            print(f"Host ({server_ip}): {message}")  # Print the server's own message
            for client, _ in clients:
                try:
                    client.send(f"Host ({server_ip}): {message}".encode('utf-8'))
                except:
                    pass

    # Start the connection handling and message sending threads
    threading.Thread(target=accept_connections, daemon=True).start()
    send_messages()

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(message)
        except ConnectionResetError:
            print('connection error')
            break

def send_messages(client_socket, client_ip):
    while True:
        message = input("Enter message: ")
        if message.lower() == 'exit':
            break
        client_socket.send(message.encode('utf-8'))
        print(f"{client_ip}: {message}")
    client_socket.close()

def main():
    choice = input("Choose option (1: Host, 2: Join): ").strip()
    
    if choice == '1':
        # Host
        port = int(input("Enter port number to host on: "))
        start_server(port)
    elif choice == '2':
        # Join
        key = input("Enter server key: ")
        try:
            server_ip, port = key.split(':')
            port = int(port)
            
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((server_ip, port))
            client_ip = socket.gethostbyname(socket.gethostname())
            
            # Start a separate thread to receive messages from the host
            threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()
            send_messages(client_socket, client_ip)
        except ValueError:
            print("No server with this key...")
            sys.exit(1)
    else:
        print("Invalid option. Please choose 1 or 2.")
        sys.exit(1)

if __name__ == "__main__":
    main()
