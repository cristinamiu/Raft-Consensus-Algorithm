from socket import *
import socket
import threading

class Server:
    def __init__(self, port, currentState = "Follower"):
        self.currentState = currentState
        self.port = port
        self.address = ("localhost", port)
        self.electionCountdown = threading.Timer(10, self.becomeCandidate)
        self.electionCountdown.start()
        


    def start(self):
        print(f"[*] Starting server on {self.address}")

        sock = socket.socket()
        sock.bind(self.address)
        sock.listen(1)

        self.becomeFollower(sock)

    def becomeFollower(self, sock):
        print(f"[*] Current state: {self.currentState}")
        print(f"[*] Listening...")

        
    def becomeCandidate(self):
        self.currentState = "Candidate"
        print(f"[*] Current state: {self.currentState}")
        # candidateCountdown = threading.Timer(3, self.becomeCandidate)
        # candidateCountdown.start()


server = Server(10000, "Follower")
server.start()


