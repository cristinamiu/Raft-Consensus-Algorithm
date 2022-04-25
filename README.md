# raft

A step by step implementation of the Raft Consensus Algorithm

## Step 1: Implement Storage, Server and Client

### 1.1 Storage

#### storage.py

```python
import json

class Storage:
    def __init__(self):
        self.data = {}
        self.op = 0
        self.k = 1
        self.v = 2

    def get(self, key):
        try:
            return self.data[key]
        except KeyError:
            return "Entry not found"

    def set(self, key, value):
        self.data[key] = value

    def delete(self, key):
        try:
            del self.data[key]
        except KeyError:
            return "Entry not found to delete"

    def handle_operation(self, command, maxsplit):
        if maxsplit == 0:
            operation = command.split(" ", maxsplit)
            operation = " ".join(operation)
        else:
            [operation, key, *value] = command.split(" ", maxsplit)
            value = " ".join(value)


        if (operation == "get"):
            response = ">> GET response: \n" + self.get(key)
        elif (operation == "set"):
            self.set(key, value)
            response = ">> SET response: \n" + key + " set to " + value
        elif (operation == "delete"):
            self.delete(key)
            response = ">> DELETE response: \n" + key + " has been deleted "
        elif (operation == "show"):
            response = ">> SHOW response: \n" + "\n".join("{!r}: {!r}".format(k, v) for k, v in self.data.items())

        else:
            response = ">> Command not recognized"

        return response

    def execute(self, command):
        response = ""
        maxsplit = command.count(" ")

        response = self.handle_operation(command, maxsplit)

        return response

```

### 1.2 Server

```python
import socket
from storage import Storage

def run_server():
    print ("[*] Recovering storage...")
    storage = Storage()
    recover(storage)

    server_address = ('localhost', 1000)
    print (f"[*] Starting server on {server_address}")

    sock = socket.socket()
    sock.bind(server_address)
    sock.listen(1)

    while True:
        print("________________________________________________________________")

        print('[*] Waiting for a connection')
        # connection, client_address = sock.accept()

        try:
            connection, client_address = sock.accept()
            print(f"[*] Connection from {client_address}")

            while True:
                operation = connection.recv(1024)

                if operation:
                    string_operation = operation.decode("utf-8")
                    print(f"[*] Received {string_operation}")

                    log_to_file(string_operation)

                    response = storage.execute(string_operation)
                    connection.sendall(response.encode('utf-8'))
                elif operation == "\n":
                    print(f"[*] No more data from {client_address}")
                    break
                else:
                    print(f"[*] No more data from {client_address}")
                    break
        except Exception:
            print(f"[*] Connection forcibly closed by {client_address}")
            connection.close()
            continue
        finally:
            connection.close()

def log_to_file(string_operation):
    f = open("storage.txt", "a")
    f.write(string_operation + '\n')
    f.close()

def recover(storage):
    f = open("storage.txt", "r")
    log = f.read()
    f.close()

    for cmd in log.split("\n"):
        storage.execute(cmd)

run_server()

```

### 1.2 Client

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('localhost', 1000)
print(f"[*] Connecting to {server_address[0]} port {server_address[1]}")
sock.connect(server_address)

while True:
    try:
        print("________________________________________________________________")
        message = input("[*] Type your message:\n    >> ")
        if message:
            print(f"[*] Sending: {message}")

            sock.sendall(message.encode('utf-8'))

            data = sock.recv(1024).decode('utf-8')
            print(f"[*] Received:\n\n{data}")
        else:
            continue

    except:
        print(f"\n[*] Closing socket")
        sock.close()
        break
```
