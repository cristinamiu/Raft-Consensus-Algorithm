def server_nodes():
    registry = {}

    f = open("logs/server_registry.txt", "r")
    logs = f.read()
    f.close()

    for node in logs.split('\n'):
        server = node.split(" ")
        if len(server) == 3:
            registry[server[0]] = (server[1], server[2])

    return registry

def get_nodes_in_network(name="ss3"):
        other_nodes = "\n".join("{!r}: {!r}".format(k, v) for k, v in server_nodes().items() if k != name)

        return "[*] Other nodes in the network: \n\n" +  other_nodes
