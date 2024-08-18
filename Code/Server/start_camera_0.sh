#!/bin/sh
while :
do
	echo 'starting camera 0'
	rpicam-vid --framerate 30 -n --exposure sport --camera 0  --width 1366 --height 768 -t 0 --inline --listen -o tcp://0.0.0.0:8889
done
