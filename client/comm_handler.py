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

TO_ML = 8002
FROM_ML = 8003

TXTFILE = "/home/gps/tele6550_final/readouts.txt"
ML_PIPE = "/tmp/ml"

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
        print("Setup UDP Recieve Socket from Client")
        
        MLsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        MLsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        
        #my_file = open(TXTFILE, "a")
    
        while(1):
            try:
                #print("Waiting on message from RPI")
                msg = sock.recv(1024).decode()
                decoded_msg= json.loads(msg)
                print(f'Got {decoded_msg}')
                temp = decoded_msg['Temp']

                sock.sendto(msg.encode('utf-8'), (MY_ADDR, TO_ML))
                print(f'Sent {temp} to ML')
                
                #currentTime = datetime.now().strftime("%H:%M:%S")
                #my_file.write(f'{currentTime} {temp}\n')
                #my_file.flush()
            except Exception as e:
                print(e)
            except KeyboardInterrupt:
                my_file.close()


def main():

    udp_recieve = udpComm(7003, False)
    udp_recieve.start()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    
    #pipe_fd = os.open("/tmp/toMl", os.O_WRONLY)
    #print("Opened Pipe to ML")

    fromMlSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    fromMlSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    fromMlSock.bind((MY_ADDR, FROM_ML))
    
    try:

        while(1):
            try:
                msg = fromMlSock.recv(1024).decode()
                decoded_msg= json.loads(msg)
                print(f'Got {decoded_msg} from ML')


                state_dict = {'State': decoded_msg['State']}
                state_to_send = json.dumps(state_dict)
                sock.sendto(state_to_send.encode('utf-8'), (CLIENT_ADDR, SEND))
                #print(f'Sent State')
            except Exception as e:
                print(f'Couldnt send State: {e}')


    except Exception as e:
        print("Exception ", e)
    

if __name__ == "__main__":
    main()
