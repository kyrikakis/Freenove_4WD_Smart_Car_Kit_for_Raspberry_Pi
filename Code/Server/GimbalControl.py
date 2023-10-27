import time
import RTIMU
import math
from servo import Servo
from threading import Thread


class GimbalControl:
    def __init__(self):
        self.is_running = False

        self.initial_pitch = 0
        self.initial_yaw = 0

        self.servo = Servo()

    def start(self):
        self.s = RTIMU.Settings("RTIMULib")
        self.imu = RTIMU.RTIMU(self.s)

        if not self.imu.IMUInit():
            raise Exception("IMU Init Failed")

        self.imu.setSlerpPower(0.02)
        self.imu.setGyroEnable(True)
        self.imu.setAccelEnable(True)
        self.imu.setCompassEnable(False)

        self.poll_interval = self.imu.IMUGetPollInterval()/1000

        self.is_running = True
        print(f'gimbal started')
        self.gimbalThread = Thread(target=self.get_data)
        self.gimbalThread.start()

        self.servo.setServoPwm('1', 90)
        self.servo.setServoPwm('2', 90)

        servo_interval = self.poll_interval #Servo interval in seconds
        lastServoTime = time.perf_counter() #Postpone servo the first time
        while self.is_running:
            timeElapsed = time.perf_counter() - lastServoTime
            if(timeElapsed > servo_interval):
                # Perform servo control here
                # For example, to set a servo to a specific angle:
                yaw = self.normalize_yaw(self.yaw)
                roll = self.normalize_combined(self.pitch, self.yaw, self.roll)
                # yaw = yaw - self.initial_yaw
                # print(f"Roll: {self.roll:.2f} degrees, Pitch: {self.pitch:.2f} degrees, Yaw: {self.yaw:.2f} degrees, SYaw: {yaw:.2f} degrees, SRoll: {roll:.2f} degrees")
                self.servo.setServoPwm('1', yaw)
                self.servo.setServoPwm('2', roll)
                lastServoTime = time.perf_counter()

    def get_data(self):
        lastReadTime = time.perf_counter() #Read the first time
        while self.is_running:
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
                    # self.yaw=self.yaw+self.initial_yaw
                    # self.pitch=self.pitch+self.initial_pitch
                    # self.roll=self.roll+self.initial_pitch
                    # print(f"Roll: {self.roll:.2f} degrees, Pitch: {self.pitch:.2f} degrees, Yaw: {self.yaw:.2f} degrees")
                    lastReadTime = time.perf_counter()

    def normalize_yaw(self, yaw):
        min_original = -90
        max_original = 90
        min_normalized = 0
        max_normalized = 180

        if yaw < min_original:
            normalized_value = min_normalized
        elif yaw > max_original:
            normalized_value = max_normalized
        else:
            # Apply the linear transformation formula
            normalized_value = ((yaw - min_original) / (max_original - min_original)) * (max_normalized - min_normalized) + min_normalized
        inverted_value = max_normalized - normalized_value
        return inverted_value
    
    def normalize_roll(self, roll):
        min_original = -60
        max_original = 5
        min_normalized = 150
        max_normalized = 85

        # roll = roll - self.initial_pitch
        if roll < min_original:
            normalized_value = min_normalized
        elif roll > max_original:
            normalized_value = max_normalized
        else:
            # Apply the linear transformation formula
            normalized_value = ((roll - min_original) / (max_original - min_original)) * (max_normalized - min_normalized) + min_normalized

        return normalized_value
    
    def normalize_pitch(self, pitch, yaw):
        min_original = -60
        max_original = 5
        # pitch = pitch - self.initial_pitch
        if yaw > 0:
            pitch = -pitch
            # pitch = pitch + self.initial_pitch
        min_normalized = 150
        max_normalized = 85

        if pitch < min_original:
            normalized_value = min_normalized
        elif pitch > max_original:
            normalized_value = max_normalized
        else:
            # Apply the linear transformation formula
            normalized_value = ((pitch - min_original) / (max_original - min_original)) * (max_normalized - min_normalized) + min_normalized

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
        normalized_roll = self.normalize_roll(roll)
        normalized_pitch = self.normalize_pitch(pitch, yaw)
        # print(f"normalized_roll: {normalized_roll}")
        # print(f"normalized_pitch: {normalized_pitch}")
        normalized_roll = roll_weight * normalized_roll
        normalized_pitch = pitch_weight * normalized_pitch
        # print(f"normalized_roll with weight: {normalized_roll}")
        # print(f"normalized_pitch with weight: {normalized_pitch}")
        normalized_value = normalized_roll + normalized_pitch

        return normalized_value

    def stop(self):
        self.is_running = False
        self.servo.setServoPwm('1', 90)
        self.servo.setServoPwm('2', 90)
        pass

if __name__ == "__main__":
    gimbal = GimbalControl()
    try:
        gimbal.start()
    except KeyboardInterrupt:
        gimbal.stop()
        pass