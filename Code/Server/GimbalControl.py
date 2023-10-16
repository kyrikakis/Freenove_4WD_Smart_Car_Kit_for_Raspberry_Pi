import time
import RTIMU
import math
from servo import Servo
from threading import Thread


class GimbalControl:
    def __init__(self):
        # self.servo = Servo()  # Initialize the Servo class

        self.s = RTIMU.Settings("RTIMULib")
        self.imu = RTIMU.RTIMU(self.s)

        if not self.imu.IMUInit():
            raise Exception("IMU Init Failed")

        self.imu.setSlerpPower(0.02)
        self.imu.setGyroEnable(True)
        self.imu.setAccelEnable(True)
        self.imu.setCompassEnable(False)

        self.poll_interval = self.imu.IMUGetPollInterval()/1000

        self.roll = 0
        self.pitch = 0
        self.yaw = 0

    def start(self):
        try:
            lastReadTime = time.perf_counter() #Read the first time
            while True:
                timeElapsed = time.perf_counter() - lastReadTime
                if(timeElapsed > self.poll_interval):
                    if self.imu.IMURead():
                        # print(f"timeElapsed: {timeElapsed}")
                        # print(f"lastReadTime: {lastReadTime}")
                        # print(f"lastServoTime: {lastServoTime}")
                        data = self.imu.getIMUData()
                        fusionPose = data["fusionPose"]
                        self.roll = math.degrees(fusionPose[0])
                        self.pitch = math.degrees(fusionPose[1])
                        self.yaw = math.degrees(fusionPose[2])
                        # print(f"Roll: {self.roll:.2f} degrees, Pitch: {self.pitch:.2f} degrees, Yaw: {self.yaw:.2f} degrees")
                        lastReadTime = time.perf_counter()
        except KeyboardInterrupt:
            pass

    def normalize_yaw(self, yaw):
        min_original = -90
        max_original = 90
        min_normalized = 0
        max_normalized = 180

        if yaw < min_original:
            normalized_value = min_original
        elif yaw > max_original:
            normalized_value = max_original
        else:
            # Apply the linear transformation formula
            normalized_value = ((yaw - min_original) / (max_original - min_original)) * (max_normalized - min_normalized) + min_normalized
        inverted_value = max_normalized - normalized_value
        return inverted_value
    
    def normalize_roll_or_pitch(self, roll):
        min_original = -60
        max_original = 5
        min_normalized = 150
        max_normalized = 85

        if roll < min_original:
            normalized_value = min_normalized
        elif roll > max_original:
            normalized_value = max_normalized
        else:
            # Apply the linear transformation formula
            normalized_value = ((roll - min_original) / (max_original - min_original)) * (max_normalized - min_normalized) + min_normalized

        return normalized_value
    
    def normalize_combined(self, pitch, yaw, roll):
        abs_yaw = abs(yaw)
        min_yaw = 0
        max_yaw = 90
        min_normalized = 150
        max_normalized = 85

        # Calculate the weight of roll and pitch based on yaw angle
        pitch_weight = (abs_yaw - min_yaw) / (max_yaw - min_yaw)
        # print(f"pitch_weight: {pitch_weight}")
        roll_weight = 1 - pitch_weight
        # print(f"roll_weight: {roll_weight}")
        # Linearly combine the effects of roll and pitch
        normalized_roll = self.normalize_roll_or_pitch(roll)
        normalized_pitch = self.normalize_roll_or_pitch(pitch)
        # print(f"normalized_roll: {normalized_roll}")
        # print(f"normalized_pitch: {normalized_pitch}")
        normalized_roll = roll_weight * normalized_roll
        normalized_pitch = pitch_weight * normalized_pitch
        # print(f"normalized_roll with weight: {normalized_roll}")
        # print(f"normalized_pitch with weight: {normalized_pitch}")
        normalized_value = (normalized_roll + normalized_pitch)

        return normalized_value

    def stop(self):
        # Clean up and stop the servos
        pass

if __name__ == "__main__":
    gimbal = GimbalControl()
    gimbalThread = Thread(target=gimbal.start)
    gimbalThread.start()

    servo = Servo()
    time.sleep(2)
    servo.setServoPwm('1', 90)
    servo.setServoPwm('2', 90)

    servo_interval = gimbal.poll_interval #Servo interval in seconds
    try:
        lastServoTime = time.perf_counter() #Postpone servo the first time
        while True:
            timeElapsed = time.perf_counter() - lastServoTime
            if(timeElapsed > servo_interval):
                # Perform servo control here
                # For example, to set a servo to a specific angle:
                yaw = gimbal.normalize_yaw(gimbal.yaw)
                roll = gimbal.normalize_combined(gimbal.pitch, gimbal.yaw, gimbal.roll)
                print(f"Roll: {gimbal.roll:.2f} degrees, Pitch: {gimbal.pitch:.2f} degrees, Yaw: {gimbal.yaw:.2f} degrees, SYaw: {yaw:.2f} degrees, SRoll: {roll:.2f} degrees")
                servo.setServoPwm('1', yaw)
                servo.setServoPwm('2', roll)
                lastServoTime = time.perf_counter()
    except KeyboardInterrupt:
        pass