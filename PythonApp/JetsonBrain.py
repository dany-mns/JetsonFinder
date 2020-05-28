#!/usr/bin/env python3

import socket
import Jetson.GPIO as GPIO
import cv2
from os import path
from threading import Thread
from Things import Motor, DistanceSensor
from adafruit_servokit import ServoKit

def gstreamer_pipeline(
    capture_width=1280,
    capture_height=720,
    display_width=1280,
    display_height=720,
    framerate=60,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )


cmd_keywords = ['photo', 'forward', 'back', 'left', 'right', 'stop', 'camera lef                                                                                                                                                             t', 'camera right', 'distance left', 'distance right', 'fast', 'slow', 'poză', '                                                                                                                                                             mergi', 'înapoi', 'stânga', 'dreapta', 'camera stânga', 'camera dreapta', 'accel                                                                                                                                                             erează', 'încetinește', 'distanță stânga', 'distanță dreapta']

GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

leftDistanceSensor = DistanceSensor(11, 13)
rightDistanceSensor = DistanceSensor(15, 16)
print("Distance sensor initialised!")

leftMotor = Motor(33, 21, 22)
rightMotor = Motor(32, 26, 24)
speed = 40
leftMotor.setSpeed(speed)
rightMotor.setSpeed(speed)
print("Motors initialized!")

# setup servo control
kit = ServoKit(channels=16)
kit.servo[0].angle = 90 # camera init position
angle = 90
print("Servomotor initialized!")

# setup camera
camera = cv2.VideoCapture(gstreamer_pipeline(flip_method=2), cv2.CAP_GSTREAMER)
print("Camera initialized!")

class TcpIp():
        def __init__(self, ip, port):
                self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_ST                                                                                                                                                             REAM)
                self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEA                                                                                                                                                             DDR, 1)
                self.serversocket.bind((ip, port))
                self.serversocket.listen(5)
                self.th_sockets = []

        def close_connection(self):
                print('Wait for server socket to close (host, port)')

                if not self.th_sockets:
                        for th in self.th_sockets:
                                th.stop()
                                th.join()

                if self.serversocket:
                        self.serversocket.close()
                        self.serversocket = None

        def process(self, client_socket, client_addr):
                global speed
                global angle
                data = client_socket.recv(1024)
                if not data:
                    print("No data.")
                else:
                    data = data.decode("utf-8")
                    if data in cmd_keywords:
                        if data in ['photo', 'poză']:
                            print(data)
                            ret, frame = camera.read()
                            cv2.imwrite("img.jpg", frame)
                            with open("img.jpg", "rb") as image:
                                image_data = image.read()
                            client_socket.sendall(image_data)
                        elif data in ['forward', 'mergi']:
                            print(data)
                            leftMotor.goForward()
                            rightMotor.goForward()
                        elif data in ['back', 'înapoi']:
                            print(data)
                            leftMotor.goBackward()
                            rightMotor.goBackward()
                        elif data in ['fast', 'accelerează']:
                            print(data)
                            speed += 10
                            if speed > 100:
                                speed = 100
                            leftMotor.setSpeed(speed)
                            rightMotor.setSpeed(speed)
                        elif data in ['slow', 'încetinește']:
                            print(data)
                            speed -= 10
                            if speed < 20:
                                speed = 20
                            leftMotor.setSpeed(speed)
                            rightMotor.setSpeed(speed)
                        elif 'stop' == data:
                            leftMotor.stop()
                            rightMotor.stop()
                        elif data in ['left', 'stânga']:
                            print(data)
                            leftMotor.stop()
                            rightMotor.goForward()
                        elif data in ['right', 'dreapta']:
                            print(data)
                            leftMotor.goForward()
                            rightMotor.stop()
                        elif data in ['distance left', 'distanță stanga']:
                            print(data)
                            print("Left distance: {:.2f} cm".format(leftDistance                                                                                                                                                             Sensor.getDistance()))
                        elif data in ['distance right', 'distanță dreapta']:
                            print(data)
                            print("Right distance: {:.2f} cm".format(rightDistan                                                                                                                                                             ceSensor.getDistance()))
                        elif data in ['camera left', 'camera stânga']:
                            print(data)
                            angle -= 20
                            if angle < 10:
                                angle = 10
                            kit.servo[0].angle = angle
                        elif data in ['camera right', 'camera dreapta']:
                            print(data)
                            angle += 20
                            if angle > 170:
                                angle = 170
                            kit.servo[0].angle = angle
                print('Receive: ' + str(data) + ' from ' + str(client_addr))
                client_socket.close()

        def run(self):
                print('====== Start Server ======')

                while True:
                        print ('Jetson Finder is waiting for your command...')

                        try:
                                client_socket, client_addr = self.serversocket.a                                                                                                                                                             ccept()
                        except Exception:
                                client_socket = None

                        if client_socket:
                                th = Thread(target=self.process, args=(client_so                                                                                                                                                             cket, client_addr, ))
                                self.th_sockets.append(th)
                                th.start()

                self.close_connection()



def main():
        server = TcpIp('192.168.0.101', 1998)
        try:
            server.run()
        except KeyboardInterrupt:
            print("Done!")
            camera.release()
            GPIO.cleanup()



if __name__ == "__main__":
        main()
