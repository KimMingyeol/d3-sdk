import json
import keyboard
from threading import Thread

class IMUListener:
    def __init__(self, clientSocket):
        self.socket = clientSocket
        packet = self.make_command('events.subscribe', {
        "events": [
            "DRIMU.imu"
        ]
        }) # subscribe to imu sensor event (i.e. IMU sensor data)
        self.socket.send(packet.encode('utf-8'))
        self.th = Thread(target=self.run)
        self.qpressed = False

    def make_command(self, command, data=None):
        packet = { 'c': command }
        if data is not None:
            packet['d'] = data
        return json.dumps(packet)

    def start(self):
        self.wfile =  open("imu_data.txt", "a")
        self.wfile.truncate(0)
        self.th.start()

    def run(self):
        while True:
            packet_rcvd = self.socket.recv(4096).decode('utf-8')
            for e in packet_rcvd.split('\n')[:-1] : # received packets could include more than one sensor event (commonly 3 events), last data(empty string) excluded
                json.dump(json.loads(e), self.wfile) # sensor event type conversion: string -> json
                self.wfile.write("\n")
            
            if keyboard.is_pressed('q'):
                break
            # print(packet_rcvd)
        self.qpressed = True

    def join(self):
        print("imu listener joined.")
        self.th.join()