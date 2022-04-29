import threading

def becomeCandidate():
    print("Enter")

    a = threading.Timer(1, becomeCandidate)
    a.start()

a=4
if a==2:
    becomeCandidate()

while a :
    if a==2:
        break
    print(2+2)
    a -= 1


