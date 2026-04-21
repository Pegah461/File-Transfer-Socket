import os
import socket
import struct

HOST = "localhost"
PORT = 9999
BUFFER_SIZE = 4096

def receive_data(sock, size):
    data = b""
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            raise ConnectionError("Connection lost while receiving data.")
        data += packet
    return data

def receive_string(sock):
    data_length = receive_data(sock, 4)
    length = struct.unpack('!I', data_length)[0]  # Unpack the length
    if length == 0:
        return ""
    return receive_data(sock, length).decode("utf-8")  # Receive the string data

def send_string(sock, string):
    encoded_string = string.encode("utf-8")
    sock.sendall(struct.pack('!I', len(encoded_string)))  # Send the length of the string
    sock.sendall(encoded_string)  # Send the string data

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
server.bind((HOST, PORT))
server.listen()

print(f"Server is listening on [{HOST}:{PORT}]...")
print("Waiting for a connection...")

client, address = server.accept()
print(f"Connection established with [{address}]")
print(f"Ready to communicate with [{address}]...")

try:
    requested_file = receive_string(client)
    print(f"Client [{address}] requested file: {requested_file}...")

    if not os.path.isfile(requested_file) or not os.path.exists(requested_file):
        print(f"File {requested_file} does not exist. Sending error message to client.")
        send_string(client, "ERROR: File not found.")
        print("Requested file does not exist.")

    else:
        file_size = os.path.getsize(requested_file)
        
        send_string(client, "OK")  # Send acknowledgment to client
        send_string(client, os.path.basename(requested_file))  # Send the file name to the client
        client.sendall(struct.pack('!Q', file_size))  # Send the file size to the client

        print(f"Sending file {requested_file} ({file_size} bytes) to client [{address}]...")

        sent_bytes = 0
        last_percent = -1

        with open(requested_file, "rb") as file:
            while True:
                data = file.read(BUFFER_SIZE)
                if not data:
                    break

                client.sendall(data)
                sent_bytes += len(data)

                percent = int((sent_bytes / file_size) * 100) if file_size > 0 else 100
                if percent != last_percent:
                    print(f"Sent {percent}% of the file to client [{address}]...")
                    last_percent = percent

        print(f"File transfer completed.")
except Exception as e:
    print(f"Server error: {e}")

finally:
    client.close()
    server.close()
    print("Server closed.")