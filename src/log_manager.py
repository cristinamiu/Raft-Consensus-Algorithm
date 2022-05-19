import threading
path = "C:/Users/crist/Documents/Projects/DA/raft/logs/"

class LogManager:
    client_lock = threading.Lock()

    def __init__(self, serverName):
        self.data = {}
        self.valid_operations = {"show" : 1, "get" : 2, "set": 3, "delete" : 2}
        self.server = serverName
        self.fileName = path + serverName + "_log.txt"
        self.last_term = 0
        self.last_index = -1
        self.logs = {}
    
    def get(self, key):
        try:
            self.last_index +=1
            return self.data[key]
        except KeyError:
            return "Entry not found"

    def set(self, key, value):
        self.data[key] = value
        self.last_index += 1

    def delete(self, key):
        try:
            del self.data[key]
            self.last_index += 1
        except KeyError:
            self.last_index += 1
            return "Entry not found to delete"

    def recoverLogs(self):
        f = open(self.fileName, "r")
        logs = f.readlines()
        f.close()

        for log in logs:
            index, term, command = log.split(" ", 2)
            # self.last_index = int(index)
            self.execute(index, term, command)
            self.last_term = int(term)
            self.updateLogs(index, term, command)

    def logCommandToFile(self, index, term, command):
        f = open(self.fileName, "a")
        f.write(f"{index} {term} {command}\n")
        f.close()

    def getLastLog(self):
        f = open(self.fileName, "r")
        logs = f.readlines()
        f.close()

        for log in logs:
            pass
        lastLog = log
        return lastLog

    @classmethod
    def extractFromLog(self, log):
        print(type(log))
        index, term, command = log.split(" ", 2)
        return index, term, command

    def getMissingEntries(self, index):
        f = open(self.fileName, "r")
        logs = f.readlines()
        f.close()
        entriesToReturn = []

        for log in logs:
            log = log.strip()
            dict = {}
            logIndex, term, command = log.split(" ", 2)
            if logIndex > index:
                dict = {"index" : logIndex, "term" : term, "command" : command}
                entriesToReturn.append(dict)
        return entriesToReturn




    def execute(self, index, term, command):
        response = ""
        validCommand = self.validateCommand(command)

        if validCommand:
            response = self.handleOperation(command)

        else:
            response = "Invalid command."

        return response

    def updateLogs(self, index, term, command):
        if "show" not in command:
            index = int(index)
            term = int(term)
            self.logs[index] = {"term": term, "cmd": command}

    def validateCommand(self, command):
        isValid = True
        operation = command.split(" ", 2)[0]
        args_number = len(command.split(" ", 2))

        if command:
            isValid = (operation in self.valid_operations) and (self.valid_operations[operation] == args_number)
        else:
            isValid = False

        return isValid

    def handleOperation(self, command):
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
                print(self.logs)
    
            else:
                response = ">> Command not recognized"

        return response

# l = LogManager("s1")
# l.recoverLogs()
# print(l.last_index)