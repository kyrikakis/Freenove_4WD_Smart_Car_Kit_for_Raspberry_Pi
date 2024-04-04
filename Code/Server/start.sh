#!/bin/sh
cd "/home/pi/Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi/Code/Server" 
pwd
while ! ifconfig | grep -F "192.168.1." > /dev/null; do 
	sleep 1
done
#bash /home/pi/start_ros2.sh &
#sudo amixer sset 'Master' 100%
./start_camera_0.sh &
sleep 3
./start_camera_1.sh &
sleep 2
sudo python main.py -tn
