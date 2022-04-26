from socket import *
import socket
import threading
from server_nodes import server_nodes
from storage import Storage

class Server:
    def __init__(self, name, port=1000):
        self.name = name
        self.port = port
        self.storage = Storage()

    def run_server(self):
        print ("[*] Recovering storage...") 
        self.storage.recover()

        server_address = ('localhost', self.port)

        f = open("logs/server_registry.txt", "a")
        f.write(self.name + " localhost " + str(self.port) + '\n')
        f.close()

        print (f"[*] Starting server on {server_address}") 

        sock = socket.socket()
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind(server_address)
        sock.listen(1)

        while True:
            print("________________________________________________________")
            print('[*] Waiting for a connection')

            connection, client_address = sock.accept()
            print(f"[*] Connection from {client_address}")

            threading.Thread(target=self.handle_client, args=(connection, self.storage, client_address)).start()
        
    def handle_client(self, connection, storage, client_address):
        while True:
            print('[**] Connected to client')

            try:
                while True:
                    operation = connection.recv(1024)

                    if operation:
                        self.handle_operation(connection, storage, operation)
                    else:
                        print(f"[*] No more data from {client_address}")
                        break

            except Exception:
                print(f"[*] Connection forcibly closed by {client_address}")
                connection.close()
                break
            
            finally:
                connection.close()

    def handle_operation(self, connection, storage, operation):
        string_operation = operation.decode("utf-8")
        print(f"[*] Received {string_operation}")

        self.storage.log_to_file(string_operation)

        response = storage.execute(string_operation)

        connection.sendall(response.encode('utf-8'))

