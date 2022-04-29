import socket
import sys
import threading
from log_manager import LogManager

class Server:
    def __init__(self, name, port):
        self.name = name
        self.port = port
        self.logManager = LogManager(self.name)
        self.serverAddress = ("localhost", port)
        self.currentTerm = 0

    def runServer(self):
        print("[*] Recovering logs...")
        self.logManager.recoverLogs()

        print(f"[*] Server started on {self.serverAddress}")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.serverAddress)
        self.sock.listen(10)

        while True:
            print("________________________________________________________")
            print('[*] Waiting for a connection')

            connection, client_address = self.sock.accept()
            print(f"[*] Connection from {client_address}")

            threading.Thread(target=self.handle_client, args=(connection, client_address)).start()

    def handle_client(self, connection, client_address):
        while True:
            try:
                while True:
                    operation = connection.recv(1024)       
                    if operation:
                        self.handle_operation(connection, operation)
                    else:
                        print(f"[*] No more data from {client_address}")
                        break       
            except Exception as e:
                print(f"[*] Connection forcibly closed by {client_address}" + str(e))
                connection.close()
                break       
            finally:
                connection.close()  

    def handle_operation(self, connection, operation):
        string_operation = operation.decode("utf-8")
        print(f"[*] Received {string_operation}")

        self.logToLocalStorage(string_operation)

        response = self.logManager.execute(self.logManager.last_index, self.currentTerm, string_operation)

        connection.sendall(response.encode('utf-8')) 

    def logToLocalStorage(self, string_operation):
        validCommand = self.logManager.validateCommand(string_operation) and ("show" not in string_operation)

        if (validCommand):
            self.logManager.logCommandToFile(self.logManager.last_index, self.currentTerm, string_operation)   
            self.logManager.updateLogs(self.logManager.last_index, self.currentTerm, string_operation)


Server(name=sys.argv[1], port=int(sys.argv[2])).runServer() 
        
