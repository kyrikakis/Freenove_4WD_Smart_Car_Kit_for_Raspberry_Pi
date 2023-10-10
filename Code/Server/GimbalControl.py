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

    poll_interval = imu.IMUGetPollInterval()
    print("Poll Interval: %d ms" % poll_interval)

    # Initialize the Servo class for controlling servos
    servo = Servo()

    try:
        while True:
            if imu.IMURead():
                data = imu.getIMUData()
                fusionPose = data["fusionPose"]
                roll = math.degrees(fusionPose[0]) -90
                pitch = math.degrees(fusionPose[1])
                yaw = math.degrees(fusionPose[2])
                print(f"Roll: {roll:.2f} degrees, Pitch: {pitch:.2f} degrees, Yaw: {yaw:.2f} degrees")

                # Perform servo control here
                # For example, to set a servo to a specific angle:
                servo.setServoPwm('0', roll)
                servo.setServoPwm('1', yaw)

                time.sleep(poll_interval/1000.0)

    except KeyboardInterrupt:
        pass
