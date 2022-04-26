import socket

class Client:
    def __init__(self, port=1000):
        self.port = port

    def start(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_address = ('localhost', self.port)
        print(f"[*] Connecting to {server_address[0]} port {server_address[1]}")
        sock.connect(server_address)

        while True:
            try:
                print(50 * "_")
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