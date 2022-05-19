class RequestVote:
    def __init__(self, currentTerm, lastLogTerm, lastLogIndex):
        self.currentTerm = currentTerm
        self.lastLogTerm = lastLogTerm
        self.lastLogIndex = lastLogIndex

    def toMessage(self):
        return "Can I count on your vote? " + str(self.currentTerm) + "-" + str(self.lastLogTerm) + "-" + str(self.lastLogIndex)

    @classmethod
    def fromMessage(self, message):
        msg = message.replace("Can I count on your vote? ", "")
        currentTerm, lastLogTerm, lastLogIndex = msg.split("-")

        return RequestVote(currentTerm,lastLogTerm,lastLogIndex)
        