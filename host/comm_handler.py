import socket
import os
import json
import threading
# import fcntl
from time import sleep
from datetime import datetime
from threading import Thread

######## THIS IS FOR ML COMMS
ML_ADDR = "127.0.0.1"
ML_PORT = 7001

ADDR = "192.168.1.8"
PORT = 7002

# txtFile = "/home/jshalke/tele6550_final/readouts.txt"
txtFile = r"C:\Users\jshal\OneDrive\School\Northeastern\TELE 6550 IoT Embedded Design\Project\tele6550_final\readouts.txt"

class States:
    COOL = -1
    OFF = 0
    HEAT = 1

State = States.OFF

class Communication(Thread):
    global state
    def __init__(self, addr, port, textFile, writeToFile):
        super().__init__()
        self.daemon = True
        self.file = open(textFile, "a")
        self.writer = writeToFile
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(1)
        #self.sock.settimeout(0.1)
        self.sock.bind((addr, port))
        self.running = True
        self.conn, self.address = None, None
        self.lastStateSent = None

    def run(self):
        print("Listening for connection\n")
        while(self.conn is None):
            try:
                self.sock.listen()
                self.conn, self.address = self.sock.accept()
            except:
                pass

        while True:
            try:
                self.getData()
                self.sendData()

            except KeyboardInterrupt:
                self.sock.close()
                return -1;
            except Exception as e:
                print(e)
                sleep(1)

    def getData(self):
        try:
            data = self.conn.recv(1024).decode('utf-8')
             
            if(len(data) != 0):
                parsed_data = json.loads(data)
                print(f'Got {parsed_data}')
                currentTime = datetime.now().strftime("%H:%M:%S")
                temp = parsed_data['temp']
                self.file.write(f'{currentTime} {temp}\n')

        except socket.error:
            pass

    def sendData(self):
        if(State != self.lastStateSent):
            try:
                sendmsg = {f'"state": {State}'}
                json_msg = json.dumps(sendmsg, default=str).encode("utf-8")
                self.conn.send(json_msg)
                print(f'SENT {State}')
                self.lastStateSent = State
            except:
                print(f'couldnt send message')


def main():

    comm_with_client = Communication(ADDR, PORT, txtFile, True)
    comm_with_client.start()
    while(1):
        pass
    #client = threading.Thread(target=communication)
    #client.start()
'''
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((ML_ADDR, ML_PORT))
        sock.listen()
        conn2, addr2 = sock.accept()
        print("Connected to ML program\n")

        while(1):
            ML_data = conn.recv(1024).decode('utf-8')
            parsed_ML_data = json.loads(ML_data)
            print(f'Got {parsed_ML_data} from ML program')
            


    except Exception as e:
        print("Exception ", e)
'''

if __name__ == "__main__":
    main()
