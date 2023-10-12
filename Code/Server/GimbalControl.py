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
    servo_interval = 0.1 #Servo interval in seconds
    time.sleep(2)

    poll_interval = imu.IMUGetPollInterval()
    print("Poll Interval: %d ms" % poll_interval)
    poll_interval = poll_interval/1000
    time.sleep(1)

    try:
        lastReadTime = time.perf_counter() - poll_interval #Read the first time
        lastServoTime = time.perf_counter() + servo_interval #Postpone servo the first time
        while True:
            if((time.perf_counter() - lastReadTime) > poll_interval):
                if imu.IMURead():
                    lastRead = time.time()
                    data = imu.getIMUData()
                    fusionPose = data["fusionPose"]
                    roll = math.degrees(fusionPose[0]) -90
                    pitch = math.degrees(fusionPose[1])
                    yaw = math.degrees(fusionPose[2])
                    print(f"Roll: {roll:.2f} degrees, Pitch: {pitch:.2f} degrees, Yaw: {yaw:.2f} degrees")

                    if((time.perf_counter() - lastServoTime) > servo_interval):
                        # Perform servo control here
                        # For example, to set a servo to a specific angle:
                        if(pitch < 85):
                            pitch = 85
                        servo.setServoPwm('0', yaw)
                        servo.setServoPwm('1', pitch)
                        lastServoTime = time.perf_counter()

    except KeyboardInterrupt:
        pass
