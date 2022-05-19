import os
path = os.path.join(os.getcwd(), 'logs', r'server-configuration.txt')
print(path)

def registerNode(sname, sport):
    serverRegistry = {}
    serverRegistry = getAllNodes()

    existingEntry = (sname, str(sport) + "\n") in serverRegistry.items()

    if not existingEntry:
        f = open("../logs/server-configuration.txt", "a")
        f.write(f"{sname} {sport}\n")

def getClusterPeers(sname):
    f = open("C:/Users/crist/Documents/Projects/DA/raft/logs/server-configuration.txt", "r")
    servers = f.readlines()

    serverRegistry = {}

    for server in servers:
        name, port = server.split(" ")
        if name != sname:
            serverRegistry[name] = port

    return serverRegistry

def getAllNodes():
    f = open("C:/Users/crist/Documents/Projects/DA/raft/logs/server-configuration.txt", "r")
    servers = f.readlines()

    serverRegistry = {}

    for server in servers:
        name, port = server.split(" ")
        serverRegistry[name] = port

    return serverRegistry


def initVoteFromPeers():
    voteFromPeers = {}
    clusterPeers = getAllNodes()

    for name, port in clusterPeers.items():
        voteFromPeers[name] = False
    
    return voteFromPeers



    

getClusterPeers("s")