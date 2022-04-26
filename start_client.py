import sys
from client import Client

Client(port=int(sys.argv[1])).start() 
