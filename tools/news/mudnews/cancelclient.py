#! /usr/bin/python
import sys
from picklerpc import client

SOCKETNAME="/MUD/rpc/news"

app = client.synconnect(SOCKETNAME, "news")

while True:
    line = sys.stdin.readline()
    if len(line) == 0:
        break
    if line.endswith("\n"):
        line = line[:-1]
    app.cancelnews(line)
