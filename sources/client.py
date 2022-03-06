#!/usr/bin/env python3.7.3
'''
Copyright © 2021 DUE TUL
@ crea  : Thursday january 21, 2021
@ modi  : Tuesday May 25, 2021
@ desc  : This modules is used to sample data from sensors
@ author: Bohao Chu
'''

import sys
import mpuDriver
import threading
import micDriver as md
import tfLite

import qwiic
import time, statistics
import tflite_runtime.interpreter as tflite
import numpy as np


ToF = qwiic.QwiicVL53L1X()
time.sleep(1)
if (ToF.sensor_init() == None): print("Laser online!\n")
time.sleep(1)
ToF.set_distance_mode(1)  # Sets Distance Mode Short (Long- Change value to 2)
time.sleep(1)
mpu9250 = mpuDriver.MPU9250()
time.sleep(1)
mpu9250.searchDevice()
time.sleep(1)


# Load the TFLite model and allocate tensors.
#interpreter = tflite.Interpreter(model_path="../tflite_model/model.tflite")
interpreter = tflite.Interpreter(model_path="../tflite_model/model.tflite",
  experimental_delegates=[tflite.load_delegate('libedgetpu.so.1')])
interpreter.allocate_tensors()

mpu_x = [0 for j in range(1000)]
mpu_y = [0 for j in range(1000)]
mpu_z = [0 for j in range(1000)]
audio_data = [0 for j in range(8000)]
dis_data = 1
def mpu():
    global mpu_x
    global mpu_y
    global mpu_z
    while True:
        acc = mpu9250.readAccel()
        mpu_x.append(acc['x'])
        mpu_y.append(acc['y'])
        mpu_z.append(acc['z'])
        del(mpu_x[0])
        del(mpu_y[0])
        del(mpu_z[0])


def dis():
    global dis_data
    last_distance = 0
    while True:
        distance = []
        for i in range(8):
            ToF.start_ranging()  # Write configuration bytes to initiate measurement
            time.sleep(.02)
            distance.append(ToF.get_distance())  # Get the result of the measurement from the sensor
            ToF.stop_ranging()
            time.sleep(.02)
        avgdistance = statistics.mean(distance)
        if last_distance - avgdistance > 1.8:
            dis_data = 0
        elif last_distance - avgdistance < -1.8:
            dis_data = 2
        else:
            dis_data = 1
        last_distance = avgdistance

def mic():
    global audio_data
    while True:
        data_chunks,data_frames,start_time = md.data_grabber(stream, 0.5)
        audio_data = data_chunks[0].tolist()

def tflit():
    global audio_data
    global dis_data
    global mpu_x
    global mpu_y
    global mpu_z
    while True:
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        # 0.26s
        merge_feature = tfLite.feature(audio_data, dis_data, mpu_x, mpu_y, mpu_z)

        # Test the model on random input data.
        # 0.045, 0.01
        start = time.time()
        interpreter.set_tensor(input_details[0]['index'], merge_feature.astype(np.float32).reshape(-1, 128, 54, 1))
        interpreter.invoke()
        # The function `get_tensor()` returns a copy of the tensor data.
        # Use `tensor()` in order to get a pointer to the tensor.
        output_data = interpreter.get_tensor(output_details[0]['index'])
        end = time.time()
        # 0.35s
        print((end-start), " : ", output_data)


if __name__=="__main__":
    stream, audio = md.audio_start()
    try:
        threads = []
        t1 = threading.Thread(target=dis)
        threads.append(t1)
        t2 = threading.Thread(target=mic)
        threads.append(t2)
        t3 = threading.Thread(target=mpu)
        threads.append(t3)
        t4 = threading.Thread(target=tflit)
        threads.append(t4)
        for t in threads:
            #t.setDaemon(True)
            t.start()
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        sys.exit()
        md.audio_end(stream, audio)
        # aa
