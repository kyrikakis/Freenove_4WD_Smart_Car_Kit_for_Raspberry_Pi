import smbus
import time
import math
import RTIMU
from servo import Servo

SETTINGS_FILE = "RTIMULib"

s = RTIMU.Settings(SETTINGS_FILE)
imu = RTIMU.RTIMU(s)

if not imu.IMUInit():
    print("IMU Init Failed")
else:
    imu.setSlerpPower(0.02)
    imu.setGyroEnable(True)
    imu.setAccelEnable(True)
    imu.setCompassEnable(False)


    # Initialize the Servo class for controlling servos
    servo = Servo()
    servo_interval = 0.4 #Servo interval in seconds
    time.sleep(1)

    poll_interval = imu.IMUGetPollInterval()
    print("Poll Interval: %d ms" % poll_interval)
    poll_interval = 0.2
    time.sleep(1)

    try:
        lastReadTime = time.perf_counter() #Read the first time
        lastServoTime = time.perf_counter() #Postpone servo the first time
        while True:
            timeElapsed = time.perf_counter() - lastReadTime
            if(timeElapsed > poll_interval):
                if imu.IMURead():
                    print(f"timeElapsed: {timeElapsed}")
                    print(f"lastReadTime: {lastReadTime}")
                    print(f"lastServoTime: {lastServoTime}")
                    lastRead = time.time()
                    data = imu.getIMUData()
                    fusionPose = data["fusionPose"]
                    roll = math.degrees(fusionPose[0])
                    pitch = math.degrees(fusionPose[1])
                    yaw = math.degrees(fusionPose[2])
                    print(f"Roll: {roll:.2f} degrees, Pitch: {pitch:.2f} degrees, Yaw: {yaw:.2f} degrees")
                    lastReadTime = time.perf_counter()

                    if((time.perf_counter() - lastServoTime) > servo_interval):
                        # Perform servo control here
                        # For example, to set a servo to a specific angle:
                        if(roll < 85):
                            roll = 85
                        print('servo moved')
                        servo.setServoPwm('0', yaw)
                        servo.setServoPwm('1', pitch)
                        lastServoTime = time.perf_counter()

    except KeyboardInterrupt:
        pass
