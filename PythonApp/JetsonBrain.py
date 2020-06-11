#!/usr/bin/env python3

import socket
import Jetson.GPIO as GPIO
import jetson.inference
import jetson.utils
import argparse
import sys
from os import path
from threading import Thread
from Things import Motor, DistanceSensor
from adafruit_servokit import ServoKit


# parse the command line
parser = argparse.ArgumentParser(description="Locate objects in a live camera stream using an object detection DNN.", 
						   formatter_class=argparse.RawTextHelpFormatter, epilog=jetson.inference.detectNet.Usage())

parser.add_argument("--network", type=str, default="ssd-mobilenet-v1", help="pre-trained model to load (see below for options)")
parser.add_argument("--overlay", type=str, default="box,labels,conf", help="detection overlay flags (e.g. --overlay=box,labels,conf)\nvalid combinations are:  'box', 'labels', 'conf', 'none'")
parser.add_argument("--threshold", type=float, default=0.5, help="minimum detection threshold to use") 
parser.add_argument("--camera", type=str, default="0", help="index of the MIPI CSI camera to use (e.g. CSI camera 0)\nor for VL42 cameras, the /dev/video device to use.\nby default, MIPI CSI camera 0 will be used.")
parser.add_argument("--width", type=int, default=1280, help="desired width of camera stream (default is 1280 pixels)")
parser.add_argument("--height", type=int, default=720, help="desired height of camera stream (default is 720 pixels)")

try:
	opt = parser.parse_known_args()[0]
except:
	print("")
	parser.print_help()
	sys.exit(0)

# load the object detection network
net = jetson.inference.detectNet(opt.network, sys.argv, opt.threshold)

# create the camera and display
camera = jetson.utils.gstCamera(opt.width, opt.height, opt.camera)
print("NN & Camera initialized!")


cmd_keywords = ['photo', 'forward', 'back', 'left', 'right', 'stop', 'camera left', 'camera right', 'distance left', 'distance right', 'fast', 'slow', 'poză', 'mergi', 'înapoi', 'stânga', 'dreapta', 'camera stânga', 'camera dreapta', 'accelerează', 'încetinește', 'distanță stânga', 'distanță dreapta']

# HW init
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

leftDistanceSensor = DistanceSensor(11, 13)
rightDistanceSensor = DistanceSensor(15, 16)
print("Distance sensor initialised!")

leftMotor = Motor(33, 21, 22)
rightMotor = Motor(32, 26, 24)
speed = 70
leftMotor.setSpeed(speed)
rightMotor.setSpeed(speed)
print("Motors initialized!")

# setup servo control
kit = ServoKit(channels=16)
kit.servo[0].angle = 90 # camera init position
angle = 90
print("Servomotor initialized!")

# setup camera
#camera = cv2.VideoCapture(gstreamer_pipeline(flip_method=2), cv2.CAP_GSTREAMER)
#print("Camera initialized!")

class TcpIp():
        def __init__(self, ip, port):
                self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
                            #ret, frame = camera.read()
                            #cv2.imwrite("img.jpg", frame)
                            #with open("img.jpg", "rb") as image:
                                #image_data = image.read()
                            #client_socket.sendall(image_data)
                            # capture the image
                            img, width, height = camera.CaptureRGBA(zeroCopy=1)
							# detect objects in the image (with overlay)
                            detections = net.Detect(img, width, height, "box,labels,conf")
							# print the detections
                            print("detected {:d} objects in image".format(len(detections)))
                            for detection in detections:
                                print(detection)
                            # save image with bouding boxes
                            jetson.utils.cudaDeviceSynchronize()
                            jetson.utils.saveImageRGBA('img.jpg', img, width, height)
                            # send image to client
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
                            print("Left distance: {:.2f} cm".format(leftDistanceSensor.getDistance()))
                        elif data in ['distance right', 'distanță dreapta']:
                            print(data)
                            print("Right distance: {:.2f} cm".format(rightDistanceSensor.getDistance()))
                        elif data in ['camera left', 'camera stânga']:
                            print(data)
                            angle -= 50
                            if angle < 10:
                                angle = 10
                            kit.servo[0].angle = angle
                        elif data in ['camera right', 'camera dreapta']:
                            print(data)
                            angle += 50
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
                                client_socket, client_addr = self.serversocket.accept()
                        except Exception:
                                client_socket = None

                        if client_socket:
                                th = Thread(target=self.process, args=(client_socket, client_addr, ))
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
