# Simple TCP File Transfer Application

This is a simple file transfer application built in Python using TCP sockets. It allows a client (client.py) to connect to a server (server.py), view the list of available files in the server directory, request a file, and download it.

## Features
* File Transfer via TCP socket
* Client can view available files on the sever once a connection is established
* File download progress bar with percentage

## How It Works
1. The server starts and listens for client connections.
2. The client attempts to connect to the server.
3. Once connected, the server sends a list of available files from its directory.
4. The client displays the list and asks the user to enter the name of the file they wish to download.
5. The server checks whether the requested file exists.
6. If the file exists, the server sends the file to the client.
7. The client saves the file as `received_file` with the original file extension.
8. Both client and server display transfer progress and success messages.

## Requirements
* Python 3.x
* No extenal libraries required

## Configuration
The program uses the following default settings:
* HOST: `localhost`
* PORT: `9999`
These values are hard-coded in both the client and server.

## How to run
1. Start server
Open a terminal in `Server` folder and run:
```bash
python server.py
```
2. Start client
Open a terminal in `Client` folder and run:
```bash
python client.py
```

## Note:
* The program allows one-time download only (it ends once a transfer is completed or connection failed)
* Place the files you want to make available for download inside the `Server` folder.
* The downloaded file is saved in the client directory as `received_file`.
