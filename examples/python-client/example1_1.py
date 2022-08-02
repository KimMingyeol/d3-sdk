from socket import *
import sys, pdb, time
from datetime import datetime
import json
from turtle import Turtle
import keyboard

# 20220726 Nkmg
# Example1: Simple Control; version 1; more than one input possible
# Type 'socat TCP-LISTEN:22023 UNIX-CONNECT:/tmp/doubleapi' on D3 terminal before run this code.

serverName = '141.223.209.154'
serverPort = 22023 # not necessarily this number, just same as the port number opened at D3(TCP LISTEN state)
clientSocket = None

ptime = None

def make_command(command, data=None, conv_str=False):
    packet = { 'c': command }
    if data is not None:
        packet['d'] = data
    return json.dumps(packet)


if __name__ == '__main__':
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    key_info = {"up": {"pressed": False, "time": None}, "down": {"pressed": False, "time": None}, "left": {"pressed": False, "time": None}, "right": {"pressed": False, "time": None}} # up down left right
    is_moving = False

    print("setting...")
    packet = make_command('base.kickstand.retract') # unlock parking
    clientSocket.send(packet.encode('utf-8'))
    time.sleep(2)
    print("setting done")

    while True:
        ctime = datetime.now()
        if keyboard.is_pressed(72):
            if key_info["up"]["pressed"] == False:
                key_info["up"]["time"] = ctime
            key_info["up"]["pressed"] = True
        else:
            key_info["up"]["time"] = None
            key_info["up"]["pressed"] = False
        
        if keyboard.is_pressed(80):
            if key_info["down"]["pressed"] == False:
                key_info["down"]["time"] = ctime
            key_info["down"]["pressed"] = True
        else:
            key_info["down"]["time"] = None
            key_info["down"]["pressed"] = False

        if keyboard.is_pressed(75):
            if key_info["left"]["pressed"] == False:
                key_info["left"]["time"] = ctime
            key_info["left"]["pressed"] = True
        else:
            key_info["left"]["time"] = None
            key_info["left"]["pressed"] = False
            
        if keyboard.is_pressed(77):
            if key_info["right"]["pressed"] == False:
                key_info["right"]["time"] = ctime
            key_info["right"]["pressed"] = True
        else:
            key_info["right"]["time"] = None
            key_info["right"]["pressed"] = False
        
        throttle = 0; turn = 0
        if key_info["up"]["pressed"] == True and key_info["down"]["pressed"] == True:
            if (key_info["up"]["time"] - key_info["down"]["time"]).total_seconds() > 0 : # up pressed later
                throttle = 1
            else:
                throttle = -1
        elif key_info["up"]["pressed"] == True:
            throttle = 1
        elif key_info["down"]["pressed"] == True:
            throttle = -1

        if key_info["left"]["pressed"] == True and key_info["right"]["pressed"] == True:
            if (key_info["left"]["time"] - key_info["right"]["time"]).total_seconds() > 0 : # left pressed later
                turn = -1
            else:
                turn = 1
        elif key_info["left"]["pressed"] == True:
            turn = -1
        elif key_info["right"]["pressed"] == True:
            turn = 1
        
        if (throttle != 0 or turn != 0) or is_moving == True:
            packet = make_command('navigate.drive', {
"throttle": throttle,
"turn": turn
})
            clientSocket.send(packet.encode('utf-8'))
            print(ctime, "command sent", throttle, turn)
        
        if throttle != 0 or turn != 0:
            is_moving = True
        else:
            is_moving = False

        time.sleep(0.2)