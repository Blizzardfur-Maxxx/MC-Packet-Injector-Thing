import socket
import threading

connected_remote_sockets = []

def send_packets(client_socket, remote_socket):
    try:
        while True:
            client_data = client_socket.recv(4096)
            if not client_data:
                break
                
            remote_socket.sendall(client_data)
            remote_data = remote_socket.recv(4096)
            if not remote_data:
                break
                
            client_socket.sendall(remote_data)
    except Exception as e:
        print("Error in send_packets:", e)
    finally:
        connected_remote_sockets.remove(remote_socket)
        remote_socket.close()


def send_message_to_all(message):
    try:
        for remote_socket in connected_remote_sockets:
            packet = b'\x03' + len(message).to_bytes(2, byteorder='big') + message.encode('utf-16be')
            remote_socket.sendall(packet)
    except Exception as e:
        print("Error in send_message_to_all:", e)

def handle_commands(remote_socket):
    while True:
        command = input("Enter command: ")
        if command.startswith("message"):
            message = command.split(" ", 1)[1]
            send_message_to_all(message)
        else:
            print("Invalid command")

def proxy_server(local_host, local_port, remote_host, remote_port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((local_host, local_port))
    server.listen(5)

    print(f"[*] Listening on {local_host}:{local_port}")

    while True:
        client_socket, addr = server.accept()
        print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
        
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((remote_host, remote_port))
        connected_remote_sockets.append(remote_socket)
        proxy_thread = threading.Thread(target=send_packets, args=(client_socket, remote_socket))
        proxy_thread.start()

        command_thread = threading.Thread(target=handle_commands, args=(remote_socket,))
        command_thread.start()

if __name__ == "__main__":
    remote_host = input("Enter remote server IP: ")
    remote_port = int(input("Enter remote server port: "))
    proxy_server('127.0.0.1', 25575, remote_host, remote_port)
