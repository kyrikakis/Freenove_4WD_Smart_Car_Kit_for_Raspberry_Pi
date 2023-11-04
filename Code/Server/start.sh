#!/bin/sh
cd "/home/skyrikakis/Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi/Code/Server" 
pwd
while ! ifconfig | grep -F "192.168.1." > /dev/null; do 
	sleep 1
done
sudo python main.py -tn
