import socket
import os
import json
import threading
import fcntl
import sys

from time import sleep
from threading import Thread


HOST_ADDR = "192.168.1.10"
HOST_PORT = 7002

TEMP_PIPE = "/tmp/temp"


class States:
    COOL = 2
    OFF = 0
    HEAT = 1

class fromBMP(Thread):
    
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.tempValue = -1
        print("In thread\n")
        
    def run(self):
        print("Looking to open temp pipe")
        pipe_fd = os.open("/tmp/temp", os.O_RDONLY)
        print("Opened temp pipe")

        while(1):
            data = os.read(pipe_fd, 1024)
            self.tempValue = data.decode('utf-8')


class toGPIO(Thread):

    def __init__(self):
        super().__init__()
        self.daemon = True
        self.curState = States.OFF
        self.lastSentState = States.OFF

    def run(self):
        print("Looking to open GPIO pipe")
        pipe_fd = os.open("/tmp/gpio", os.O_WRONLY)
        print("Opened GPIO pipe")

        while(1):
            if(self.curState != self.lastSentState):
                os.write(pipe_fd, self.curState.to_bytes(4,byteorder='little'))
                print(f'Sent {self.curState} to GPIO')
                self.lastSentState = self.curState
            sleep(1)

class udpComm(Thread):

    def __init__(self, port, send):
        super().__init__()
        self.daemon = True
        self.send = send
        self.port = port
        self.recievedState = None

    def run(self):
            self.recieveLoop()

    def recieveLoop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.bind((HOST_ADDR, self.port))
        print("Setup UDP Recieve Socket")
    
        while(1):
            print("Waiting on message from Computer")
            msg = sock.recv(1024).decode()
            decoded_msg= json.loads(msg)
            print(f'Got {decoded_msg}')
            self.recievedState = decoded_msg['State']


def main():
    

    from_sensor = fromBMP()
    from_sensor.start()

    to_gpio = toGPIO()
    to_gpio.start()

    udp_send = udpComm(7003, False)
    udp_send.start()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    #sock.bind((HOST_ADDR, HOST_PORT))
    

    try:
        while(1):
            try:
                print(from_sensor.tempValue)
                if(from_sensor.tempValue > 1):
                    temp_dict = {'Temp': from_sensor.tempValue}
                    temp_to_send = json.dumps(temp_dict, default=str).encode('utf-8')
                    sock.sendto(temp_to_send, (HOST_ADDR, HOST_ADDR))
            except Exception as e:
                print(f'Couldnt send temp: {e}')
            sleep(1)


    except KeyboardInterrupt:
        return -1
    


if __name__ == "__main__":
    main()
