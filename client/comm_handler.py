import socket
import os
import json
import threading
import fcntl
from time import sleep

HOST_ADDR = "0.0.0.0"
HOST_PORT = 7002


def communication():
    print("Hello")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((CLIENT_ADDR, CLIENT_PORT))
        s.listen()
        conn, addr = s.accept()
        print("Received an connection")
        
        try:
            while(1):
                data = s.recv(1024).decode()
                print(f'Got {data} from client')
        
        except KeyboardInterrupt:                                                                                                                                 pass

        return -1;

def send_data(socket, data):
    print("\nSending this data: ", data)
    socket.sendall(data)

def main():
    tmplist = []
    dic = {}

    #client = threading.Thread(target=communication)
    #client.start()

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((HOST_ADDR,HOST_PORT))
        
        msg = {'temp': 70}
        json_msg = json.dumps(msg, default=str).encode("utf-8")
        
        while(1):
            server.send(json_msg)
            sleep(3)

        '''
        # Connected
        while True:
            incoming_json_data = sock.recvfrom(1024)
            json_data = incoming_json_data[0].decode()
            print(json_data)
            print("\n")

            
            new_json_data = json.loads(json_data)

            print(new_json_data, "\n")

            packaged_good = json.dumps(new_json_data)  
        '''

    except Exception as e:
        print("Exception ", e)


if __name__ == "__main__":
    main()
