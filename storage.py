import threading

class Storage:
    client_lock = threading.Lock()

    def __init__(self):
        self.data = {}
        self.valid_operations = {"show" : 1, "get" : 2, "set": 3, "delete" : 2}

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

    def execute(self, command):
        response = ""
        valid_command = self.validate_command(command)

        if not valid_command:
            return "Invalid command"
        else:
            response = self.handle_operation(command)

        return response

    def handle_operation(self, command):
        operands = command.split(" ", 2)
        operation = operands[0]

        with self.client_lock:
            if (operation == "get"):
                key = operands[1]
                response = ">> GET response: \n" + self.get(key)

            elif (operation == "set"):
                key, value = operands[1:3]
                self.set(key, value)
                response = ">> SET response: \n" + key + " set to " + value

            elif (operation == "delete"):
                key = operands[1]
                self.delete(key)
                response = ">> DELETE response: \n" + key + " has been deleted "

            elif (operation == "show"):
                response = ">> SHOW response: \n" + "\n".join("{!r}: {!r}".format(k, v) for k, v in self.data.items()) 
    
            else:
                response = ">> Command not recognized"

        return response

    def recover(self):
        f = open("logs/storage.txt", "r")
        logs = f.read()
        f.close()

        for cmd in logs.split("\n"):
            self.execute(cmd)

    def log_to_file(self, command):
        valid = self.validate_command(command)
        if not valid:
            return

        f = open("logs/storage.txt", "a")
        f.write(command + '\n')
        f.close()

    def validate_command(self, command):
        isValid = True
        operation = command.split(" ", 2)[0]
        args_number = len(command.split(" ", 2))

        if command:
            isValid = (operation in self.valid_operations) and (self.valid_operations[operation] == args_number)
        else:
            isValid = False

        return isValid
        




        