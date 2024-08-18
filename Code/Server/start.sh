#!/bin/sh
pwd
while ! ifconfig | grep -F "192.168.1." > /dev/null; do 
	sleep 1
done
#bash /home/pi/start_ros2.sh &
#sudo amixer sset 'Master' 100%
cd /home/pi/mediamtx && ./mediamtx /home/pi/Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi/Code/Server/mediamtx.yml &
#sleep 3
#./start_camera_1.sh &
sleep 1
cd "/home/pi/Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi/Code/Server" && \n
sudo python main.py -tn
