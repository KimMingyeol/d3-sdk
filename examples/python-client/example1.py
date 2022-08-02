from socket import *
import sys, pdb, time
from datetime import datetime
import json
from pynput import keyboard

# 20220726 Nkmg
# Example1: Simple Control; version 0; cannot get more than one input
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

def on_press(key):
    global ptime
    global clientSocket
    throttle = 0
    turn = 0
    ctime = datetime.now()
    if ptime is None or (ctime - ptime).total_seconds() >= 0.2:
        ptime = ctime

        if key==keyboard.Key.right:
            turn = 1
        elif key==keyboard.Key.left:
            turn = -1
        
        if key==keyboard.Key.up:
            throttle = 1
        elif key==keyboard.Key.down:
            throttle = -1
        
        packet = make_command('navigate.drive', {
"throttle": throttle,
"turn": turn
})
        clientSocket.send(packet.encode('utf-8'))

def on_release(key):
    global ptime
    global clientSocket
    ptime = None
    packet = make_command('navigate.drive', {
"throttle": 0,
"turn": 0
})
    clientSocket.send(packet.encode('utf-8'))
    if key == keyboard.Key.esc:
        # Stop listener
        return False

if __name__ == '__main__':
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    
    print("setting...")
    packet = make_command('base.kickstand.retract') # unlock parking
    clientSocket.send(packet.encode('utf-8'))
    time.sleep(2)
    print("setting done")

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()