import threading

class Storage:
    client_lock = threading.Lock()

    def __init__(self):
        self.data = {}
        self.op = 0
        self.k = 1
        self.v = 2

    def get(self, key):
        try:
            return self.data[key]
        except KeyError:
            return "Entry not found"

    def set(self, key, value):
        self.data[key] = value

    def delete(self, key):
        try:
            del self.data[key]
        except KeyError:
            return "Entry not found to delete"

    def handle_operation(self, command, maxsplit):
        if maxsplit == 0:
            operation = command.split(" ", maxsplit)
            operation = " ".join(operation)
        else:
            [operation, key, *value] = command.split(" ", maxsplit)
            value = " ".join(value)

        with self.client_lock:
            if (operation == "get"):
                response = ">> GET response: \n" + self.get(key)
            elif (operation == "set"):
                self.set(key, value)
                response = ">> SET response: \n" + key + " set to " + value
            elif (operation == "delete"):
                self.delete(key)
                response = ">> DELETE response: \n" + key + " has been deleted "
            elif (operation == "show"):
                response = ">> SHOW response: \n" + "\n".join("{!r}: {!r}".format(k, v) for k, v in self.data.items()) 
    
            else:
                response = ">> Command not recognized"

        return response

    def execute(self, command):
        response = ""
        maxsplit = command.count(" ")

        if maxsplit == 0:
            operation = command.split(" ", maxsplit)
            operation = " ".join(operation)
        else:
            [operation, key, *value] = command.split(" ", maxsplit)
            value = " ".join(value)

        with self.client_lock:
            if (operation == "get"):
                response = ">> GET response: \n" + self.get(key)
            elif (operation == "set"):
                self.set(key, value)
                response = ">> SET response: \n" + key + " set to " + value
            elif (operation == "delete"):
                self.delete(key)
                response = ">> DELETE response: \n" + key + " has been deleted "
            elif (operation == "show"):
                response = ">> SHOW response: \n" + "\n".join("{!r}: {!r}".format(k, v) for k, v in self.data.items()) 
    
            else:
                response = ">> Command not recognized"

        return response 




        