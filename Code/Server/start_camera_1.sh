#!/bin/sh
while :
do
	echo 'starting camera 1'
	rpicam-vid --framerate 30 -n --camera 1 --hdr sensor --width 1366 --height 768 -t 0 --inline --listen -o tcp://0.0.0.0:8888
done
