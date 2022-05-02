import socket
import sys
import threading
import time
from log_manager import LogManager

class Server:
    def __init__(self, name, port):
        self.name = name
        self.port = port
        self.logManager = LogManager(self.name)
        self.serverAddress = ("localhost", port)
        self.currentTerm = 0
        self.isLeader = False

    def send(self, port, message):
        message = self.name + "@" + message
        toAddress = ('localhost', port)

        peerSocket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            peerSocket.connect(toAddress)
            encodedMessage = message.encode('utf-8')

            try:
                print("Sending message")
                peerSocket.sendall(encodedMessage)
                time.sleep(0.5)
                peerSocket.close()
            except Exception as e:
                print("Failed to send message" + str(e))
        except Exception as e:
            print("Failed to send message - Connection failed" + str(e))
        finally:
            peerSocket.close()

    def runServer(self):
        print("[*] Recovering logs...")
        self.logManager.recoverLogs()

        print(f"[*] Server started on {self.serverAddress}")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.serverAddress)
        self.sock.listen(6000)

        if (self.name == "s1"):
            self.send(10001, "Hello, world!")

        while True:
            print("________________________________________________________")
            print('[*] Waiting for a connection')

            connection, client_address = self.sock.accept()
            print(f"[*] Connection from {client_address}")

            threading.Thread(target=self.handleConnection, args=(connection, client_address)).start()

    def handleConnection(self, connection, client_address):
        while True:
            try:
                while True:
                    request = connection.recv(1024)       
                    if request:
                        self.handleRequest(connection, request)
                    else:
                        # print(f"[*] No more data from {client_address}")
                        break       
            except Exception as e:
                print(f"[*] Connection closed by {client_address}" + str(e))
                connection.close()
                break       
            finally:
                connection.close()  

    def handleRequest(self, connection, request):
        address, string_operation = request.decode("utf-8").split("@")
        print(f"[*] Received from {address} : {string_operation}")

        if address == "client":
            response = self.handleLogOperation(connection, string_operation) 
            connection.sendall(response.encode('utf-8'))

        else:
            if string_operation == "Hello, world!": 
                self.send(10000, "Hello, world back!")


    def handleLogOperation(self, connection, string_operation):
        if self.isLeader:
            self.logToLocalStorage(string_operation)

            response = self.logManager.execute(self.logManager.last_index, self.currentTerm, string_operation)
        else:
            response = "Sorry, I am not the leader."

        return response 


    def logToLocalStorage(self, string_operation):
        validCommand = self.logManager.validateCommand(string_operation) and ("show" not in string_operation)

        if (validCommand):
            self.logManager.logCommandToFile(self.logManager.last_index, self.currentTerm, string_operation)   
            self.logManager.updateLogs(self.logManager.last_index, self.currentTerm, string_operation)


Server(name=sys.argv[1], port=int(sys.argv[2])).runServer() 
        
