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

def get_file_list():
    files = []
    for item in os.listdir('.'):
        if os.path.isfile(item):
            files.append(item)
    files.sort()
    return files

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket
server.bind((HOST, PORT))
server.listen()

print(f"\nServer is listening on [{HOST}:{PORT}]...")
print("Waiting for a connection...")

client, address = server.accept()
print(f"\nConnection established with [{address}]")

try:

    files_avail = get_file_list()
    file_list_msg = "\n".join(files_avail) if files_avail else "No files available."
    send_string(client, file_list_msg)  # Send the list of available files to the client
    print("\nSent list of available files to client.")
    print("Waiting for client's file request...")

    requested_file = receive_string(client)
    print(f"\nClient [{address}] requested file: [{requested_file}]...")

    if not os.path.isfile(requested_file) or not os.path.exists(requested_file):
        print(f"\nFile {requested_file} does not exist. Sending error message to client.")
        send_string(client, "ERROR: File not found.")
        print("Requested file does not exist.")

    else:
        file_size = os.path.getsize(requested_file)
        
        send_string(client, "OK")  # Send acknowledgment to client
        send_string(client, os.path.basename(requested_file))  # Send the file name to the client
        client.sendall(struct.pack('!Q', file_size))  # Send the file size to the client

        print(f"\nSending file {requested_file} ({file_size} bytes) to client [{address}]...")

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
                    bar_length = 30
                    filled = int(bar_length * sent_bytes / file_size) if file_size > 0 else bar_length
                    bar = "#" * filled + "-" * (bar_length - filled)
                    print(f"\rTransferring: [{bar}] {percent}%", end="")
                    last_percent = percent

        print("\n\nFile transfer completed.")
except Exception as e:
    print(f"Server error: {e}")

finally:
    client.close()
    server.close()
    print("\nServer closed.")