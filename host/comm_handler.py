import socket
import os
import json
import threading
import fcntl
from time import sleep
from datetime import datetime
from threading import Thread

######## THIS IS FOR ML COMMS
ML_ADDR = "127.0.0.1"
ML_PORT = 7001

CLIENT_ADDR = "192.168.1.10"
MY_ADDR = "192.168.1.8"
SEND = 7002
RECIEVE = 7003

TXTFILE = "/home/gps/tele6550_final/readouts.txt"

class States:
    COOL = -1
    OFF = 0
    HEAT = 1


class udpComm(Thread):

    def __init__(self, port, send):
        super().__init__()
        self.daemon = True
        self.send = send
        self.port = port
        self.recievedTemp = None

    def run(self):
            self.recieveLoop()

    def recieveLoop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.bind((MY_ADDR, RECIEVE))
        print("Setup UDP Recieve Socket")

        my_file = open(TXTFILE, "a")
    
        while(1):
            try:
                #print("Waiting on message from RPI")
                msg = sock.recv(1024).decode()
                decoded_msg= json.loads(msg)
                print(f'Got {decoded_msg}')
                temp = decoded_msg['Temp']
                currentTime = datetime.now().strftime("%H:%M:%S")
                my_file.write(f'{currentTime} {temp}\n')
            except Exception as e:
                print(e)


def main():

    udp_recieve = udpComm(7003, False)
    udp_recieve.start()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    
    
    try:

        tst_state = States.OFF

        while(1):
            try:
                state_dict = {'State': tst_state}
                state_to_send = json.dumps(state_dict)
                sock.sendto(state_to_send.encode('utf-8'), (CLIENT_ADDR, SEND))
                #print(f'Sent State')
                sleep(4)
            except Exception as e:
                print(f'Couldnt send State: {e}')


    except Exception as e:
        print("Exception ", e)
    

if __name__ == "__main__":
    main()
