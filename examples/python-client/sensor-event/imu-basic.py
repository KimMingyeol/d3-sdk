from socket import *
import sys, pdb, os, signal
import json, time
import multiprocessing
import numpy as np
import matplotlib.pyplot as plt

# 20220729 Nkmg
# IMU-basic: Tracking IMU sensor data from d3 robot
# Type 'socat TCP-LISTEN:22022 UNIX-CONNECT:/tmp/doubleapi' on D3 terminal before run this code.

rtp_queue = None
rtp = None
clientSocket = None
max_datanum = 50

def make_command(command, data=None):
    packet = { 'c': command }
    if data is not None:
        packet['d'] = data
    return json.dumps(packet)

def json_data_filter(json_data):
    # quaternion
    ret = {"qx": [], "qy": [], "qz": [], "qw": []}
    for e in json_data:
        ret["qx"].append(e["data"]["quat"]["x"])
        ret["qy"].append(e["data"]["quat"]["y"])
        ret["qz"].append(e["data"]["quat"]["z"])
        ret["qw"].append(e["data"]["quat"]["w"])
    ret["qx"] = np.array(ret["qx"])
    ret["qy"] = np.array(ret["qy"])
    ret["qz"] = np.array(ret["qz"])
    ret["qw"] = np.array(ret["qw"])
    return ret

def rtplot_process(q):
    # quaternion IMU data: x, y, z, w
    data_updated = {"qx":{"x":np.arange(max_datanum), "y":np.zeros(max_datanum)}, "qy":{"x":np.arange(max_datanum), "y":np.zeros(max_datanum)}, "qz":{"x":np.arange(max_datanum), "y":np.zeros(max_datanum)}, "qw":{"x":np.arange(max_datanum), "y":np.zeros(max_datanum)}}

    plt.ion() # plot: interactive mode on
    figure, ax = plt.subplots(2, 2, figsize=(10,8))
    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9, wspace=0.3, hspace=0.4)
    
    line_qx, = ax[0,0].plot(data_updated["qx"]["x"], data_updated["qx"]["y"], 'ko-', markersize = 0.8, linewidth = 0.3)
    ax[0,0].set_title("quat x", fontsize= 10)
    ax[0,0].set_ylim(-1,1)

    line_qy, = ax[0,1].plot(data_updated["qy"]["x"], data_updated["qy"]["y"], 'ko-', markersize = 0.8, linewidth = 0.3)
    ax[0,1].set_title("quat y", fontsize= 10)
    ax[0,1].set_ylim(-1,1)

    line_qz, = ax[1,0].plot(data_updated["qz"]["x"], data_updated["qz"]["y"], 'ko-', markersize = 0.8, linewidth = 0.3)
    ax[1,0].set_title("quat z", fontsize= 10)
    ax[1,0].set_ylim(-1,1)

    line_qw, = ax[1,1].plot(data_updated["qw"]["x"], data_updated["qw"]["y"], 'ko-', markersize = 0.8, linewidth = 0.3)
    ax[1,1].set_title("quat w", fontsize= 10)
    ax[1,1].set_ylim(-1,1)

    while(True):
        if q.qsize() > 0:
            json_data = q.get()
            imu_data = json_data_filter(json_data)

            data_updated["qx"]["y"] = imu_data["qx"]
            data_updated["qx"]["x"] = np.arange(data_updated["qx"]["y"].size)
            
            data_updated["qy"]["y"] = imu_data["qy"]
            data_updated["qy"]["x"] = np.arange(data_updated["qy"]["y"].size)
            
            data_updated["qz"]["y"] = imu_data["qz"]
            data_updated["qz"]["x"] = np.arange(data_updated["qz"]["y"].size)
            
            data_updated["qw"]["y"] = imu_data["qw"]
            data_updated["qw"]["x"] = np.arange(data_updated["qw"]["y"].size)
        
        line_qx.set_data(data_updated["qx"]["x"], data_updated["qx"]["y"])
        line_qy.set_data(data_updated["qy"]["x"], data_updated["qy"]["y"])
        line_qz.set_data(data_updated["qz"]["x"], data_updated["qz"]["y"])
        line_qw.set_data(data_updated["qw"]["x"], data_updated["qw"]["y"])

        figure.canvas.draw()
        figure.canvas.flush_events()

        time.sleep(0.01)

def join_rtplot_process(): # executed when the whole process ended
    if rtp_queue is not None:
        rtp_queue.close()
        rtp_queue.join_thread()
        print("queue closed.")
    if rtp is not None:
        rtp.join()
        print("joined.")

def close_socket():
    if clientSocket is not None:
        clientSocket.close()
        print("socket closed.")

def sigint_handler(signum, frame): # ctrl-c handler
    os.system('cls')
    print("exited...")
    join_rtplot_process()
    close_socket()
    exit(1)

if __name__ == '__main__':
    serverName = '141.223.209.154'
    serverPort = 22022 # not necessarily this number, just same as the port number opened at D3(TCP LISTEN state)

    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))

    packet = make_command('events.subscribe', {
    "events": [
        "DRIMU.imu"
    ]
    }) # subscribe to imu sensor event (i.e. IMU sensor data)
    clientSocket.send(packet.encode('utf-8'))

    imu_json_data = []
    most_recent = None

    # Use of multiprocessing to run plot on another process
    rtp_queue = multiprocessing.Queue() # queue to keep data shared among processes
    rtp = multiprocessing.Process(target=rtplot_process, args=(rtp_queue,)) # create a separate process for plotting
    rtp.start()
    # Ctrl-c handler set
    signal.signal(signal.SIGINT, sigint_handler)

    while True:
        packet_rcvd = clientSocket.recv(4096).decode('utf-8')
        for e in packet_rcvd.split('\n')[:-1] : # received packets could include more than one sensor event (commonly 3 events), last data(empty string) excluded
            most_recent = json.loads(e) # sensor event type conversion: string -> json
            imu_json_data.append(most_recent)
        imu_json_data = imu_json_data[-max_datanum:] # keep at most 50(=max_datanum) events
        # os.system('cls')
        # print(most_recent) # these make the plot changes slower

        if rtp_queue.qsize() > 0 : # only one json data stored in the shared queue
            while rtp_queue.empty() == False:
                rtp_queue.get()
        rtp_queue.put(imu_json_data) # put most recent data on the shared queue
    
    join_rtplot_process()
    close_socket()