from socket import *
import sys, pdb
import json
import time

# 20220726 Nkmg
# Example0: Dancing Robot
# Type 'socat TCP-LISTEN:22023 UNIX-CONNECT:/tmp/doubleapi' on D3 terminal before run this code.

def make_command(command, data=None):
    packet = { 'c': command }
    if data is not None:
        packet['d'] = data
    return json.dumps(packet)

serverName = '141.223.209.154'
serverPort = 22023 # not necessarily this number, just same as the port number opened at D3(TCP LISTEN state)

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

tick = True

packet = make_command('base.kickstand.retract') # unlock parking
clientSocket.send(packet.encode('utf-8'))

time.sleep(2)

while(True):
    if tick:
        packet = make_command('base.pole.stand') # pole up
    if not tick:
        packet = make_command('base.pole.sit') # pole down
    clientSocket.send(packet.encode('utf-8'))

    packet = make_command('base.turnBy', {
  "degrees": 90,
  "degreesWhileDriving": 30
}) # turn by 90 degree
    clientSocket.send(packet.encode('utf-8'))
    time.sleep(1)
    tick = not tick

# print("command send done")