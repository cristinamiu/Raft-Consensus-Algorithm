# raft
A simple implementation of the Raft Consensus Algorithm

## Start the servers

Open four terminals and start sequently using the following comands:

```bash
python server.py s1 10000
python server.py s2 10001
python server.py s3 10002
python server.py s4 10003
```

Wait until a leader is chosen and start a client connecting to port 10000 with id 1:

```bash
python client.py 10000 1
```
Now you can use commands like the ones below:

```bash
get b
set r 77
delete b
show
```
