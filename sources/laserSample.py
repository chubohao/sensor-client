import qwiic
import time, statistics

ToF = qwiic.QwiicVL53L1X()

if (ToF.sensor_init() == None):  # Begin returns 0 on a good init
    print("Sensor online!\n")

ToF.set_distance_mode(1)  # Sets Distance Mode Short (Long- Change value to 2)

distance = []  # Initialize list

last_distance = 0
now_distance = 0

while True:
    start = time.time()

    try:
        for i in range(10):
            ToF.start_ranging()  # Write configuration bytes to initiate measurement
            time.sleep(.02)
            distance.append(ToF.get_distance())  # Get the result of the measurement from the sensor
            ToF.stop_ranging()
            time.sleep(.02)
        avgdistance = statistics.mean(distance)
        if last_distance - avgdistance > 1.8:
            print("Left")
        elif last_distance - avgdistance < -1.8:
            print("Right")
        end = time.time()
        last_distance = avgdistance
        print("Distance(mm): %s avgDistance(mm): %.2f  Hz: %.5f" % (distance[len(distance) - 1], avgdistance, (end - start)))
        distance = []

    except Exception as e:
        print(e)

    #signalrate = ToF.get_signal_rate()
    #rangestatus = ToF.get_range_status()
