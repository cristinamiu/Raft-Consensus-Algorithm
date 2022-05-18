import math
import socket
import sys
import threading
import time
from log_manager import LogManager
from cluster_manager import getClusterPeers, initVoteFromPeers, registerNode

class Server:
    def __init__(self, name, port):
        self.name = name
        self.port = port
        self.logManager = LogManager(self.name)
        self.serverAddress = ("localhost", port)
        self.currentTerm = 0
        self.isLeader = False
        self.alreadyVoted = False

        self.voteFromPeers = initVoteFromPeers()

        self.electionCountdown = threading.Timer(10, self.startElection)
        self.electionCountdown.start()

    def runServer(self):
        print("[*] Recovering logs...")
        self.logManager.recoverLogs()

        registerNode(self.name, self.port)

        print(f"[*] Server started on {self.serverAddress}")


        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.serverAddress)
        self.sock.listen(6000)

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
            if string_operation == "Can I count on your vote this term?":
                if not self.alreadyVoted:
                    response = "Count on me"
                    port = self.getPortOfServer(address)
                    self.send(port, response)
                    self.alreadyVoted = True
                    self.electionCountdown.cancel()
                    print("[*] Forever Follower")

            if string_operation == "Count on me":
                self.voteFromPeers[address] = True

                if (self.getNumberOfVotes() ) >= math.ceil(self.getNumberOfPeers()/2):
                    self.electionCountdown.cancel()
                    self.isLeader = True
                    print("[*] Forever Leader")

                print(f"[*] Votes: {self.getNumberOfVotes()} -  Nodes: {self.getNumberOfPeers()}")
                

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

    def send(self, port, msg):
        message = self.name + "@" + msg
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

    def startElection(self):
        if not self.isLeader:
            print("[*] Starting election...")
            self.voteFromPeers[self.name] = True
            self.alreadyVoted = True

            message = "Can I count on your vote this term?"

            for name, port in getClusterPeers(self.name).items():
                self.send(int(port), message) 

            self.electionCountdown.cancel()
            self.electionCountdown = threading.Timer(2, self.startElection)
            self.electionCountdown.start()
        elif self.isLeader:
            self.electionCountdown.cancel()

    def getPortOfServer(self, sname):
        response = 0
        for name, port in getClusterPeers(self.name).items():
            if name == sname:
                response = port
        return int(response)

    def getNumberOfVotes(self):
        return len(list(filter(lambda x: x is True, self.voteFromPeers.values())))

    def getNumberOfPeers(self):
        return len(getClusterPeers(self.name)) + 1


Server(name=sys.argv[1], port=int(sys.argv[2])).runServer() 
        
