#!/bin/sh
while :
do
	echo 'starting camera 1'
	rpicam-vid --framerate 30 -n --exposure sport --camera 1 --width 1280 --height 720 -t 0 --inline --listen -o tcp://0.0.0.0:8210
done
