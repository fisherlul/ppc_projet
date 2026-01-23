import socket
import json
import os

HOST = "127.0.0.1"
PORT = 5000

def main():
    msg = {
        "type": "register",
        "role": "predator",
        "pid": os.getpid()
    }

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.send(json.dumps(msg).encode())

    response = s.recv(1024).decode()
    print("[PREDATOR] response from env:", response)

    s.close()

if __name__ == "__main__":
    main()
