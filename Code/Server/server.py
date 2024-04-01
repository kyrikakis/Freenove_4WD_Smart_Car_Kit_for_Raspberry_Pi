#!/usr/bin/python 
# -*- coding: utf-8 -*-
import io
import math
import socket
import  numpy as np
import struct
import time
# from picamera2 import Picamera2,Preview
# from picamera2.encoders import JpegEncoder
# from picamera2.outputs import FileOutput
# from picamera2.encoders import Quality
from threading import Condition
import fcntl
import  sys
import threading
from Motor import *
from servo import *
#from Led import *
from Buzzer import *
from ADC import *
from Thread import *
from Light import *
from Ultrasonic import *
from Line_Tracking import *
from threading import Timer
from threading import Thread
from Command import COMMAND as cmd
from MatrixMode import MATRIX_MODE
import RPi.GPIO as GPIO
from matrix_display import CustomLEDMatrixController
# from GimbalControl import GimbalControl
import subprocess

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

class Server:
    def __init__(self):
        self.PWM=Motor()
        self.servo=Servo()
        #self.led=Led()
        self.ultrasonic=Ultrasonic()
        self.buzzer=Buzzer()
        self.adc=Adc()
        self.light=Light()
        self.infrared=Line_Tracking()
        self.display=CustomLEDMatrixController()
        # self.gimbal=GimbalControl()
        self.tcp_Flag = True
        self.sonic=False
        self.Light=False
        self.Light=False
        self.Line=False
        self.Mode = 'one'
        self.endChar='\n'
        self.intervalChar='#'
        self.rotation_flag = False
        self.matrix_mode=MATRIX_MODE.NONE
        self.head_azimuth=90
        self.head_elevation=90
        # self.camera = Picamera2()
        # self.camera.configure(self.camera.create_video_configuration(main={"size": (600, 277)}))
        # self.camera.framerate_range = (30, 40)
        # self.camera.framerate = 40
        subprocess.call("espeak -v greek -a 170 \"Γειά σου Σάμερ! Τι κάνεις? Είμαι το Ρομπότ!\"", shell= True)
    def get_interface_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(),
                                            0x8915,
                                            struct.pack('256s',b'wlan0'[:15])
                                            )[20:24])
    def StartTcpServer(self):
        HOST=str(self.get_interface_ip())
        self.server_socket1 = socket.socket()
        self.server_socket1.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT,1)
        self.server_socket1.bind((HOST, 5000))
        self.server_socket1.listen(1)
        self.server_socket = socket.socket()
        self.server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT,1)
        self.server_socket.bind((HOST, 7000))
        self.server_socket.listen(1)
        self.server_socket2 = socket.socket()
        self.server_socket2.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT,1)
        self.server_socket2.bind((HOST, 8888))
        self.server_socket2.listen(1)
        print('Server address: '+HOST)

    def StopTcpServer(self):
        try:
            self.connection.close()
            self.connection1.close()
            self.connection2.close()
        except Exception as e:
            print ('\n'+"No client connection")

    def Reset(self):
        self.StopTcpServer()
        self.StartTcpServer()
        # self.camera.stop_recording()
        # self.camera.close()
        # self.InitiVideoConn1=Thread(target=self.initVideoConnection1)
        # self.InitiVideoConn2=Thread(target=self.initVideoConnection2)
        # self.SendVideo=Thread(target=self.sendvideo)
        self.ReadData=Thread(target=self.readdata)
        # self.InitiVideoConn1.start()
        # self.InitiVideoConn2.start()
        # self.SendVideo.start()
        self.ReadData.start()
    def send(self,data):
        self.connection1.send(data.encode('utf-8'))
    def initVideoConnection1(self):
        try:
            self.connection,self.client_address = self.server_socket.accept()
            self.connection=self.connection.makefile('wb')
            print ("Video connection successful !")
        except Exception as e:
            print('Video connection exception: ' + e)
            pass
        self.server_socket.close()
        print ("socket video connected ... ")
    def initVideoConnection2(self):
        try:
            self.connection2,self.client_address2 = self.server_socket2.accept()
            self.connection2=self.connection2.makefile('wb')
            print ("Video2 connection successful !")
        except Exception as e:
            print('Video2 connection exception: ' + e)
            pass
        self.server_socket2.close()
        print ("socket video2 connected ... ")
    # def sendvideo(self):
        # output = StreamingOutput()
        # encoder = JpegEncoder(q=90)
        # self.camera.start_recording(encoder, FileOutput(output),quality=Quality.VERY_HIGH)
        # while True:
        #     with output.condition:
        #         output.condition.wait()
        #         frame = output.frame
        #         lenFrame = len(output.frame)
        #         lengthBin = struct.pack('<I', lenFrame)
        #     try:
        #         self.connection.write(lengthBin)
        #         self.connection.write(frame)
        #     except Exception as e:
        #         pass

        #     try:
        #         self.connection2.write(lengthBin)
        #         self.connection2.write(frame)
        #     except Exception as e:
        #         pass

    def stopMode(self):
        try:
            stop_thread(self.infraredRun)
            self.PWM.setMotorModel(0,0,0,0)
        except:
            pass
        try:
            stop_thread(self.lightRun)
            self.PWM.setMotorModel(0,0,0,0)
        except:
            pass
        try:
            stop_thread(self.ultrasonicRun)
            self.PWM.setMotorModel(0,0,0,0)
            self.servo.setServoPwm('1',90)
            self.servo.setServoPwm('2',83)
        except:
            pass
        try:
            self.gimbal.stop()
            stop_thread(self.gimbalRun)
            self.servo.setServoPwm('1',90)
            self.servo.setServoPwm('2',90)
        except:
            pass
        self.sonic=False
        self.Light=False
        self.Line=False         
        self.send('CMD_MODE'+'#1'+'#'+'0'+'#'+'0'+'\n')
        self.send('CMD_MODE'+'#3'+'#'+'0'+'\n')
        self.send('CMD_MODE'+'#2'+'#'+'000'+'\n')           
    def readdata(self):
        try:
            try:
                self.connection1,self.client_address1 = self.server_socket1.accept()
                print ("Client connection successful !")
            except:
                print ("Client connect failed")
            restCmd=""
            self.server_socket1.close()

            voice_interval = 0.8
            last_voice_time = time.perf_counter()
            while True:
                time_elapsed = time.perf_counter() - last_voice_time
                if(time_elapsed > voice_interval):
                    if(self.Mode == 'speak1'):
                        subprocess.call("espeak -v greek -a 170 \"Είμαι το Ρομπότ! Πού είναι η Σάμερ;\"", shell= True)
                        self.Mode='one'
                    elif(self.Mode == 'speak2'):
                        subprocess.call("espeak -v greek -a 170 \"Τι μπορώ να κάνω για σένα;\"", shell= True)
                        self.Mode='one'
                    elif(self.Mode == 'speak3'):
                        subprocess.call("espeak -v greek -a 170 \"Θέλεις να παίξουμε; Μπορώ να τρέχω και να με κυνηγάς, Έλα Έλα!\"", shell= True)
                        self.Mode='one'
                    elif(self.Mode == 'speak4'):
                        subprocess.call("espeak -v greek -a 170 \"Το Ρομπότ νυστάζει, πάμε για ύπνο;\"", shell= True)
                        self.Mode='one'
                    elif(self.Mode == 'speak5'):
                        subprocess.call("espeak -v greek -a 170 \"Μου αρέσει πολύ να τρέχω μέσα στο σπίτι!\"", shell= True)
                        self.Mode='one'

                try:
                    AllData=restCmd+self.connection1.recv(1024).decode('utf-8')
                except:
                    if self.tcp_Flag:
                        self.Reset()
                    break
                print(AllData)
                if len(AllData) < 5:
                    restCmd=AllData
                    if restCmd=='' and self.tcp_Flag:
                        self.Reset()
                        break
                restCmd=""
                if AllData=='':
                    break
                else:
                    cmdArray=AllData.split("\n")
                    if(cmdArray[-1] != ""):
                        restCmd=cmdArray[-1]
                        cmdArray=cmdArray[:-1]

                for oneCmd in cmdArray:
                    data=oneCmd.split("#")
                    if data==None:
                        continue
                    elif cmd.CMD_MODE in data:
                        if data[1]=='one' or data[1]=="0":
                            self.stopMode()
                            self.Mode='one'
                        elif data[1]=='two' or data[1]=="1":
                            self.stopMode()
                            self.Mode='two'
                            self.lightRun=Thread(target=self.light.run)
                            self.lightRun.start()
                            self.Light = True
                            self.lightTimer = threading.Timer(0.3, self.sendLight)
                            self.lightTimer.start()
                        elif data[1]=='three' or data[1]=="3":
                            self.stopMode()
                            self.Mode='three'
                            self.ultrasonicRun=threading.Thread(target=self.ultrasonic.run)
                            self.ultrasonicRun.start()
                            self.sonic=True
                            self.ultrasonicTimer = threading.Timer(0.2,self.sendUltrasonic)
                            self.ultrasonicTimer.start()
                        elif data[1]=='four' or data[1]=="2":
                            self.stopMode()
                            self.Mode='four'
                            self.gimbalRun=threading.Thread(target=self.gimbal.start)
                            self.gimbalRun.start()
                            # self.infraredRun=threading.Thread(target=self.infrared.run)
                            # self.infraredRun.start()
                            # self.Line=True
                            # self.lineTimer = threading.Timer(0.4,self.sendLine)
                            # self.lineTimer.start()

                    elif (cmd.CMD_MOTOR in data) and self.Mode=='one':
                        try:
                            data1=int(data[1])
                            data2=int(data[2])
                            data3=int(data[3])
                            data4=int(data[4])
                            if data1==None or data2==None or data2==None or data3==None:
                                continue
                            self.PWM.setMotorModel(data1,data2,data3,data4)
                        except:
                            pass
                    elif (cmd.CMD_M_MOTOR in data) and self.Mode=='one':
                        try:
                            data1=int(data[1])
                            data2=int(data[2])
                            data3=int(data[3])
                            data4=int(data[4])

                            LX = -int((data2 * math.sin(math.radians(data1))))
                            LY = int(data2 * math.cos(math.radians(data1)))
                            RX = int(data4 * math.sin(math.radians(data3)))
                            RY = int(data4 * math.cos(math.radians(data3)))

                            FR = LY - LX + RX
                            FL = LY + LX - RX
                            BL = LY - LX - RX
                            BR = LY + LX + RX


                            if data1==None or data2==None or data2==None or data3==None:
                                continue
                            self.PWM.setMotorModel(FL,BL,FR,BR)
                        except:
                            pass
                    elif (cmd.CMD_CAR_ROTATE in data) and self.Mode == 'one':
                        try:

                            data1 = int(data[1])
                            data2 = int(data[2])
                            data3 = int(data[3])
                            data4 = int(data[4])
                            set_angle = data3
                            if data4 == 0:
                                try:
                                    stop_thread(Rotate_Mode)
                                    self.rotation_flag = False
                                except:
                                    pass
                                LX = -int((data2 * math.sin(math.radians(data1))))
                                LY = int(data2 * math.cos(math.radians(data1)))
                                RX = int(data4 * math.sin(math.radians(data3)))
                                RY = int(data4 * math.cos(math.radians(data3)))

                                FR = LY - LX + RX
                                FL = LY + LX - RX
                                BL = LY - LX - RX
                                BR = LY + LX + RX


                                if data1 == None or data2 == None or data2 == None or data3 == None:
                                    continue
                                self.PWM.setMotorModel(FL, BL, FR, BR)
                            elif self.rotation_flag == False:
                                self.angle = data[3]
                                try:
                                    stop_thread(Rotate_Mode)
                                except:
                                    pass
                                self.rotation_flag = True
                                Rotate_Mode = Thread(target=self.PWM.Rotate, args=(data3,))
                                Rotate_Mode.start()
                        except:
                            pass
                    elif cmd.CMD_CAMERA in data:
                        try:
                            data1 = int(data[1])
                            data2 = int(data[2])
                            if data1 == None or data2 == None:
                                continue
                            self.head_azimuth=180-data1
                            self.head_elevation=data2
                            if(data2<83):
                                self.head_elevation=83
                            elif(data2>150):
                                self.head_elevation=150
                            self.servo.setServoPwm('1',self.head_azimuth)
                            self.servo.setServoPwm('2',self.head_elevation)
                        except:
                            pass

                    # elif cmd.CMD_LED in data:
                    #     try:
                    #         data1=int(data[1])
                    #         data2=int(data[2])
                    #         data3=int(data[3])
                    #         data4=int(data[4])
                    #         if data1==None or data2==None or data2==None or data3==None:
                    #             continue
                    #         self.led.ledIndex(data1,data2,data3,data4)
                    #     except:
                    #         pass
                    # elif cmd.CMD_LED_MOD in data:
                    #     self.LedMoD=data[1]
                    #     if self.LedMoD== '0':
                    #         try:
                    #             stop_thread(Led_Mode)
                    #         except:
                    #             pass
                    #     if self.LedMoD == '1':
                    #         try:
                    #             stop_thread(Led_Mode)
                    #         except:
                    #             pass
                    #         # self.led.ledMode(self.LedMoD)
                    #         time.sleep(0.1)
                    #         # self.led.ledMode(self.LedMoD)
                    #     else :
                    #         try:
                    #             stop_thread(Led_Mode)
                    #         except:
                    #             pass
                    #         time.sleep(0.1)
                    #         Led_Mode=Thread(target=self.led.ledMode,args=(data[1],))
                    #         Led_Mode.start()
                    elif cmd.CMD_SONIC in data:
                        if data[1]=='1':
                            self.sonic=True
                            self.ultrasonicTimer = threading.Timer(0.5,self.sendUltrasonic)
                            self.ultrasonicTimer.start()
                        else:
                            self.sonic=False
                    elif cmd.CMD_BUZZER in data:
                        try:
                            self.buzzer.run(data[1])
                        except:
                            pass
                    elif cmd.CMD_LIGHT in data:
                        if data[1]=='1':
                            self.Light=True
                            self.lightTimer = threading.Timer(0.3,self.sendLight)
                            self.lightTimer.start()
                        else:
                            self.Light=False
                    elif cmd.CMD_POWER in data:
                        ADC_Power=self.adc.recvADC(2)*3
                        try:
                            self.send(cmd.CMD_POWER+'#'+str(round(ADC_Power, 2))+'\n')
                        except:
                            pass
                    elif cmd.CMD_MATRIX_MOD in data:
                        last_voice_time = time.perf_counter()
                        if data[1] == '1':
                            self.Mode='speak1'
                        elif data[1] == '2':
                            self.Mode='speak2'
                        elif data[1] == '3':
                            self.Mode='speak3'
                        elif data[1] == '4':
                            self.Mode='speak4'
                        elif data[1] == '5':
                            self.Mode='speak5'
                        elif data[1] == '0':
                            self.Mode='one' #reset to cmd.CMD_MOTOR mode
                        # if data[1] == '1':
                        #     if self.gimbal.is_running == False:
                        #         self.gimbal.initial_yaw=self.head_azimuth
                        #         self.gimbal.initial_pitch=self.head_elevation
                        #         self.gimbalRun=threading.Thread(target=self.gimbal.start)
                        #         self.gimbalRun.start()
                        # else:
                        #     self.gimbal.stop()
                    elif cmd.CMD_SERVO in data:
                        try:
                            data1 = int(data[1])
                            data2 = int(data[2])
                            if data1 == None or data2 == None:
                                continue
                            if(data1 == 0):
                                self.head_azimuth=data2+12
                            elif(data1 == 1):
                                self.head_elevation=data2
                            if(self.head_elevation<83):
                                self.head_elevation=83
                            elif(self.head_elevation>150):
                                self.head_elevation=150
                            self.servo.setServoPwm('1',self.head_azimuth)
                            self.servo.setServoPwm('2',self.head_elevation)
                        except Exception as e:
                            print(e)
                            pass

        except Exception as e:
            print(e)
        self.StopTcpServer()
    def sendUltrasonic(self):
        if self.sonic==True:
            ADC_Ultrasonic=self.ultrasonic.get_distance()
            #print('distanse: '+str(ADC_Ultrasonic))
            try:
                self.send(cmd.CMD_MODE+"#"+"3"+"#"+str(ADC_Ultrasonic)+'\n')
            except:
                self.sonic=False
            self.ultrasonicTimer = threading.Timer(0.23,self.sendUltrasonic)
            self.ultrasonicTimer.start()
    def sendLight(self):
        if self.Light==True:
            ADC_Light1=self.adc.recvADC(0)
            ADC_Light2=self.adc.recvADC(1)
            try:
                self.send("CMD_MODE#1"+'#'+str(ADC_Light1)+'#'+str(ADC_Light2)+'\n')
            except:
                self.Light=False
            self.lightTimer = threading.Timer(0.17,self.sendLight)
            self.lightTimer.start()
    def sendLine(self):
        if self.Line==True:
            Line1= 1 if GPIO.input(14) else 0
            Line2= 1 if GPIO.input(15) else 0
            Line3= 1 if GPIO.input(23) else 0
            try:
                self.send("CMD_MODE#2"+'#'+str(Line1)+str(Line2)+str(Line3)+'\n')
            except:
                self.Line=False
            self.LineTimer = threading.Timer(0.20,self.sendLine)
            self.LineTimer.start()
    def Power(self):
        while True:
            ADC_Power=self.adc.recvADC(2)*3
            try:
                self.send(cmd.CMD_POWER+'#'+str(round(ADC_Power, 2))+'\n')
            except:
                pass
            time.sleep(3)
            if ADC_Power < 6.5:
                for i in range(4):
                    self.buzzer.run('1')
                    time.sleep(0.1)
                    self.buzzer.run('0')
                    time.sleep(0.1)
            elif ADC_Power< 7:
                for i in range(2):
                    self.buzzer.run('1')
                    time.sleep(0.1)
                    self.buzzer.run('0')
                    time.sleep(0.1)
            else:
                self.buzzer.run('0')               
    def Display(self):
        self.display.animation=MATRIX_MODE.HAPPY
        self.display.eyes_smile()
        while True:
            if self.matrix_mode==MATRIX_MODE.HAPPY:
                self.display.eyes_smile()
            elif self.matrix_mode==MATRIX_MODE.BLINK:
                self.display.eyes_blink()


if __name__=='__main__':
    pass

