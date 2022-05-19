import ast

class AppendEntries:
    def __init__(self, currentTerm, previousIndex, previousTerm, entries):
        self.currentTerm = currentTerm
        self.previousIndex = previousIndex
        self.previousTerm = previousTerm
        self.entries = entries

    def toMessage(self):
        return "AppendEntries " + str(self.currentTerm) + "-" + str(self.previousIndex) + "-" + str(self.previousTerm) + "-" + str(self.entries)

    @classmethod
    def fromMessage(self, message):
        msg = message.replace("AppendEntries ", "")
        currentTerm, previousIndex, previousTerm, entries = msg.split("-")
        entries = ast.literal_eval(entries)

        return AppendEntries(currentTerm, previousIndex, previousTerm, entries)