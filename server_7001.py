import socket as s
import sys

# Create a TCP/IP socket
sock = s.socket(s.AF_INET, s.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 7001) # L33T: TOOL -> 7001
print("staring tools server")
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

def recvall():
    BUFF_SIZE = 4096 # 4 KiB
    data = b''
    while True:
        part = sock.recv(BUFF_SIZE)
        data += part
        if len(part) < BUFF_SIZE:
            break # end of data
    return data

while True:
    # Wait for connection
    connection, client_address = sock.accept()

    try:
        print("user connected")
        data = recvall()
        #data += data.decode('utf-8')
        print(data)
    finally:
        # Clean up the connection
        connection.close()
