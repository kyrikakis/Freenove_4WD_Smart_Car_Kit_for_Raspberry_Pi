#!/bin/sh
cd "/home/pi/Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi/Code/Server" 
pwd
while ! ifconfig | grep -F "192.168.1." > /dev/null; do 
	sleep 1
done
#bash /home/pi/start_ros2.sh &
#sudo amixer sset 'Master' 100%
# libcamera-vid -t 0 --width 640 --height 480 --inline --listen -o tcp://0.0.0.0:8888 &
sudo python main.py -tn
