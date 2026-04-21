import socket
import struct
import os
import time

HOST = "localhost"
PORT = 9999
BUFFER_SIZE = 4096
SAVE_AS = "received_file"
MAX_RETRIES = 10
DELAY = 5  # seconds

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

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket

try:

    connected = False
    retries = MAX_RETRIES
    while retries > 0 and not connected:
        try:
            print(f"\nAttempting to connect to server [{HOST}:{PORT}]... ({MAX_RETRIES - retries + 1}/{MAX_RETRIES})")
            client.connect((HOST, PORT))  # Replace with the server's address and port
            connected = True
            print(f"\nConnected to server [{HOST}:{PORT}]...")

        except (ConnectionRefusedError, ConnectionError) as e:
            retries -= 1
            if retries > 0:
                print(f"Connection failed. Retrying in {DELAY} seconds...")
                time.sleep(DELAY)
            else:
                print("Failed to connect to the server after multiple attempts.")
                raise ConnectionError("Unable to connect to the server after multiple attempts.")

    avail_files = receive_string(client)
    print("\nAvailable files on server:")
    print("--------------------------------")
    print(avail_files)
    print("--------------------------------")

    requested_file = input("Enter the name of the file you want to receive: ").strip()
    send_string(client, requested_file)  # Send the requested file name to the server

    response = receive_string(client)

    if response.startswith("ERROR"):
        message = response.split(":", 1)[1].strip()
        print(message)

    elif response == "OK":
        file_name = receive_string(client)
        file_size = struct.unpack('!Q', receive_data(client, 8))[0]  # Receive the file size
        print(f"\nReceiving file {file_name} ({file_size} bytes) from server...")

        save_name = SAVE_AS
        ext = os.path.splitext(file_name)[1]
        if ext:
            save_name += ext

        received_bytes = 0
        last_percent = -1

        with open(save_name, "wb") as file:
            while received_bytes < file_size:
                chunk = client.recv(min(BUFFER_SIZE, file_size - received_bytes))
                if not chunk:
                    raise ConnectionError("Connection lost while receiving file.")
                file.write(chunk)
                received_bytes += len(chunk)

                percent = int((received_bytes / file_size) * 100) if file_size > 0 else 100
                if percent != last_percent:
                    bar_length = 30
                    filled = int(bar_length * received_bytes / file_size) if file_size > 0 else bar_length
                    bar = "#" * filled + "-" * (bar_length - filled)
                    print(f"\rDownloading: [{bar}] {percent}%", end="")
                    last_percent = percent

        print("\n\nFile received successfully.")
        print(f"File saved as: {save_name}")

    else:
        print("Unexpected response from server.")


except Exception as e:
    print(f"Client error: {e}")

finally:
    client.close()
    print("\nClient closed.")