#!/usr/bin/python3

import cv2
from picamera2 import Picamera2

picam1 = Picamera2(1)
picam1.controls.FrameRate = 30
picam1.controls.AeExposureMode = 1 #Short
video_config1 = picam1.create_video_configuration(main={"format":"XRGB8888", "size": (1024, 576)})
picam1.configure(video_config1)

picam0 = Picamera2(0)
picam0.controls.FrameRate = 30
picam0.controls.AeExposureMode = 1 #Short
video_config0 = picam0.create_video_configuration(main={"format":"XRGB8888", "size": (1024, 576)})
picam0.configure(video_config0)

picam1.start()
picam0.start()

writer = cv2.VideoWriter("appsrc ! video/x-raw, format=BGR ! queue ! videoconvert ! x264enc insert-vui=1 \
                         speed-preset=veryfast tune=zerolatency ! h264parse ! mpegtsmux ! tcpserversink host=0.0.0.0 port=8889", cv2.CAP_GSTREAMER, 0, 30.0, (2048, 576)) 

while True:

    img1 = picam1.capture_array()
    img0 = picam0.capture_array()

    h_img = cv2.hconcat([img0, img1])
    height, width = h_img.shape[:2]
    # print("image size: ", width, height)
    # print("Type:",type(h_img))
    # print("Shape of Image:", h_img.shape)
    # print('Total Number of pixels:', h_img.size)
    # print("Image data type:", h_img.dtype)
    writer.write(h_img[:,:,0:3])
    cv2.waitKey(1)