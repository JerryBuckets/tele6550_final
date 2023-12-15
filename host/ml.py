#!/usr/bin/python3
import numpy as np
import tensorflow as tf
import os
import fcntl
import sys
import socket
import json

from random import random

from tensorflow.keras import layers
from tensorflow.keras import models

N = 100000

MAX = 24
MIN = 20

training_input = np.zeros(shape=(N,1))
training_output = np.zeros(shape=(N,1))

for i in range(N):
    temp = random()*40
    training_input[i] = [temp]

    if temp < MAX:
        if temp > MIN:
            training_output[i] = 1
    else:
        training_output[i] = 0

model = models.Sequential();
model.add(layers.Dense(12, input_shape=(1,), activation='relu'))
model.add(layers.Dense(1))

model.summary()

model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])

model.fit(training_input, training_output, epochs=1)

O = 10

#TXTFILE = "/home/gps/tele6550_final/readouts.txt"
'''
try:
    os.mkfifo("/tmp/toMl", mode=0o666)
except Exception as e:
    print(f'Couldnt make pipe: {e}')
    

pipe_fd = os.open("/tmp/toMl", os.O_RDONLY)
print("Opened ML Pipe")
'''

TO_ML = 8002
FROM_ML = 8003
MY_ADDR = "192.168.1.8"

fromComSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
fromComSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
fromComSock.bind((MY_ADDR, TO_ML))


toComSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
toComSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)


class States:
    COOL = -1
    OFF = 0
    HEAT = 1

sendState = States.OFF

while(1):
    try:
        msg = fromComSock.recv(1024).decode()
        decoded_msg= json.loads(msg)
        temp = decoded_msg['Temp']
        print(f'Got Temp = {temp}')

        #data = os.read(pipe_fd, 1024).decode('utf-8')
        #print(f'Got {data}')
    except Exception as e:
        print(f'Couldnt get data from pipe: {e}')

    model_out = (abs(model.predict([temp])).round())
    print(f'Model Val: {model_out[0]}')

    if ((model_out) < 0.5):
        if (temp > MAX):
            sendState = States.COOL
        elif (temp < MIN):
            sendState = States.HEAT
    else:
        sendState = States.OFF
    
    state_dict= {'State': sendState}
    send_msg = json.dumps(state_dict)
    toComSock.sendto(send_msg.encode('utf-8'), (MY_ADDR, FROM_ML))




