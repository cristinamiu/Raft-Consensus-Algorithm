import math
import socket
import sys
import threading
import time
from log_manager import LogManager
from cluster_manager import getClusterPeers, initVoteFromPeers, registerNode
from RequestVote import RequestVote
from AppendEntries import AppendEntries
import ast

class Server:
    def __init__(self, name, port):
        self.name = name
        self.port = port

        self.logManager = LogManager(self.name)
        print("[*] Recovering logs...")
        self.logManager.recoverLogs()

        self.serverAddress = ("localhost", port)
        self.currentTerm = self.logManager.last_term
        self.isLeader = False
        self.alreadyVoted = False
        self.lastVotedInTerm = -1
        self.lastLeader = None

        self.voteFromPeers = initVoteFromPeers()

        self.electionCountdown = threading.Timer(10, self.startElection)
        self.electionCountdown.start()

        self.canCandidate = True

        self.heartbeatTimer = None

    def runServer(self):
        
        print("[*] Current term: " + str(self.currentTerm))
        registerNode(self.name, self.port)

        print(f"[*] Server started on {self.serverAddress}")


        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.serverAddress)
        self.sock.listen(6000)

        while True:
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
                # print(f"[*] Connection closed by {client_address}" + str(e))
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
            if string_operation.split("? ")[0] == "Can I count on your vote":
                requestVote = RequestVote.fromMessage(string_operation)

                if int(self.lastVotedInTerm) < int(requestVote.currentTerm) and (not self.isLeader):
                    self.electionCountdown.cancel()
                    response = "Count on me"
                    port = self.getPortOfServer(address)
                    self.send(port, response)
                    print("[*] Forever Follower")

            if string_operation == "Count on me":
                self.voteFromPeers[address] = True

                if (self.getNumberOfVotes() ) >= math.ceil(self.getNumberOfPeers()/2):
                    self.electionCountdown.cancel()
                    self.isLeader = True
                    print("[*] Forever Leader")
                    print(self.voteFromPeers)
                    self.sendHeartbeat()

                print(f"[*] Votes: {self.getNumberOfVotes()} -  Nodes: {self.getNumberOfPeers()}")

            if string_operation.split(" ")[0] == "AppendEntries":
                self.isLeader = False
                self.canCandidate = False
                self.lastLeader = address
                response = "I like application"
                appendEntries = AppendEntries.fromMessage(string_operation)
                self.currentTerm = appendEntries.currentTerm

                lastLog = self.logManager.getLastLog()
                print("Last log: ", lastLog)

                lastIndex, lastTerm, lastCommand = LogManager.extractFromLog(lastLog)      

                if lastIndex == appendEntries.previousIndex and lastTerm == appendEntries.previousTerm:
                    response = "I am up to date"
                    port = self.getPortOfServer(address)
                    self.send(port, response)

                elif lastIndex < appendEntries.previousIndex:
                    if (len(appendEntries.entries) == 0):
                        response = "GiveEntriesAfterIndex " + lastIndex
                        print(response)
                        port = self.getPortOfServer(address)
                        self.send(port, response)
                    else:
                        response = "I am up to date"
                        print(appendEntries.entries)
                        for entry in appendEntries.entries:
                            print(entry["index"])
                            newEntry = entry["index"] + " " + entry["term"] + " " + entry["command"]
                            self.logNewEntry(entry["index"], entry["term"], entry["command"])
                        port = self.getPortOfServer(address)
                        self.send(port, response)


            if string_operation.split(" ")[0] == "GiveEntriesAfterIndex":
                if self.isLeader:
                    index = string_operation.split(" ")[1]
                    entries = self.logManager.getMissingEntries(index)
                    print(entries)
                    response = AppendEntries(self.currentTerm, self.logManager.last_index, self.logManager.last_term, entries).toMessage()
                    port = self.getPortOfServer(address)
                    self.send(port, response)


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

    def logNewEntry(self, index, term, command):
        self.logManager.logCommandToFile(index, term, command)


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
        if not self.isLeader and self.canCandidate:
            print("[*] Starting election...")
            self.voteFromPeers[self.name] = True
            self.currentTerm += 1
            self.lastVotedInTerm = self.currentTerm

            message = RequestVote(self.currentTerm, self.logManager.last_term, self.logManager.last_index).toMessage()

            self.broadcast(message)

            self.electionCountdown.cancel()
            self.electionCountdown = threading.Timer(5, self.startElection)
            self.electionCountdown.start()
        elif self.isLeader:
            self.electionCountdown.cancel()

    def sendHeartbeat(self):
        print("Sending heartbeat...")
        if self.isLeader:
            message = AppendEntries(self.currentTerm, self.logManager.last_index, self.logManager.last_term, []).toMessage()
            self.broadcast(message)
        self.heartbeatTimer = threading.Timer(2, self.sendHeartbeat)
        self.heartbeatTimer.start()

    def broadcast(self, message):
        for name, port in getClusterPeers(self.name).items():
            self.send(int(port), message) 

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
        
