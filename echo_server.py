from http import client
import socket 
import threading
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
        print("________________________________________________________")
        print('[*] Waiting for a connection')

        connection, client_address = sock.accept()
        print(f"[*] Connection from {client_address}")

        threading.Thread(target=handle_client, args=(connection, storage, client_address)).start()
        
def handle_client(connection, storage, client_address):
    while True:
        print('[**] Connected to client')

        try:
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
            break
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
