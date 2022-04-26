from socket import *
# import socket
import threading
from server_nodes import get_nodes_in_network
from storage import Storage
import ast

class Server:
    def __init__(self, name, port=1000):
        self.name = name
        self.port = port
        self.storage = Storage()
    
    def tell(self, message, to_server_address):
        print(f"connecting to {to_server_address[0]} port {to_server_address[1]}")

        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect(to_server_address)

        try:
            print(f"sending {message}")
            self.client_socket.sendall(message.encode('utf-8'))
        except:
            print(f"closing socket")
            self.client_socket.close()

    def run_server(self):
        # print ("[*] Recovering storage...") 
        # self.storage.recover()

        server_address = ('localhost', self.port)

        f = open("logs/server_registry.txt", "a")
        f.write(self.name + " localhost " + str(self.port) + '\n')
        f.close()

        print (f"[*] Starting server on {server_address}") 

        print(get_nodes_in_network())

        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_socket.bind(server_address)
        self.server_socket.listen(1)


        while True:
            print("________________________________________________________")
            print('[*] Waiting for a connection')

            connection, client_address = self.server_socket.accept()
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
        command = operation.decode("utf-8")
        print(f"[*] Received {command}")

        # self.storage.log_to_file(string_operation)

        if command == "log_length?":
            response = ">> Log length: " + str(len(self.storage.log))

        elif command.split(" ")[0] == "log_length":
            catch_up_start_index = int(command.split(" ")[1])

            if len(self.storage.log) > catch_up_start_index:
                response = ">> You need to catch up the following logs: " + str(self.storage.log[catch_up_start_index:])
            else:
                response = ">> Your logs are at least as good as mine!"

        elif command.split(" ")[0] == "catch_up_logs":
            logs_to_append = ast.literal_eval(command.split("catch_up_logs ")[1])
            [storage.execute(self.storage.log) for log in logs_to_append]

            response = "Caught up. Thanks!"

        elif command == "show_log":
            response = str(self.storage.log)

        elif command == "youre_the_leader":
            self.broadcast('log_length?')

        else:
            response = storage.execute(command)

        connection.sendall(response.encode('utf-8'))

    def broadcast(self, message):
        for other_server_address in get_nodes_in_network():
            self.tell(message, to_server_address=other_server_address)


