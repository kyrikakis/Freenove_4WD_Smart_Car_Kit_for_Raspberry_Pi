import time
from PCA9685 import PCA9685
import smbus
import RTIMU
import math
from servo import Servo

class GimbalControl:
    def __init__(self):
        self.servo_pan = Servo()
        self.servo_tilt = Servo()

        SETTINGS_FILE = "RTIMULib"
        self.imu = RTIMU.RTIMU(RTIMU.Settings(SETTINGS_FILE))

        if not self.imu.IMUInit():
            raise Exception("IMU Init Failed")

        self.imu.setSlerpPower(0.02)
        self.imu.setGyroEnable(True)
        self.imu.setAccelEnable(True)
        self.imu.setCompassEnable(False)

        self.poll_interval = self.imu.IMUGetPollInterval()

    def start(self):
        try:
            while True:
                if self.imu.IMURead():
                    data = self.imu.getIMUData()
                    fusionPose = data["fusionPose"]
                    roll = math.degrees(fusionPose[0]) - 90
                    pitch = math.degrees(fusionPose[1])
                    yaw = math.degrees(fusionPose[2])

                    # Map the angles to servo positions (adjust these mappings as needed)
                    pan_angle = yaw  # Map yaw to pan servo
                    tilt_angle = roll  # Map pitch to tilt servo

                    # Limit servo angles to prevent over-rotation (adjust these limits as needed)
                    pan_angle = max(-90, min(90, pan_angle))
                    tilt_angle = max(-90, min(90, tilt_angle))

                    # Set servo positions using the setServoPulse method from PCA9685
                    self.servo_pan.setServoPwm(pan_angle)
                    self.servo_tilt.setServoPulse(tilt_angle)

                    print(f"Pan: {pan_angle:.2f} degrees, Tilt: {tilt_angle:.2f} degrees")
                    time.sleep(self.poll_interval / 1000.0)

        except KeyboardInterrupt:
            pass

    def stop(self):
        # Clean up and stop the servos
        self.servo_pan.cancel()
        self.servo_tilt.cancel()

if __name__ == "__main__":
    gimbal = GimbalControl()
    gimbal.start()
