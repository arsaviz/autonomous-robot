# Remote Car Robot Controler Using Object detection and Computer Vision

this repository contains the code I used for my thesis:

Thesis: Building a mobile robot and routing and stopping it using computer vision techniques and machine learning based on environmental circumstances
</br>
Student: Alireza Saviz
</br>
Supervisort: <a href="https://scholar.google.com/citations?user=vmyY_5kAAAAJ&hl=en">Dr. Alireza Yazdizadeh</a>
</br>
Score: 20/20 (A+)

# how to run this code:
You need to do several steps in order to make this code run on your setup
## 1. making the robot car
I used these parts for my robot:
- a robot car chassis with 4 geared motors
- esp32 wifi/Bluetooth module
- L298N motor driver
- SRF05 ultrasonic sensor
- rechargeable battery
- mobile holder
- Android mobile phone
- breadboards and jumper cables

assemble the chassis and make the circuit using this diagram as a reference: 
</br>
<img src="images/circuit_diagram.png">
</br>
and the complete robot should look something like this:
</br>
<img src="images/car.png">

## 2. load the esp module code
- download the Arduino ide and install it ( if not already installed! )
- change the code and enter your SSID and password of your router or mobile hotspot
- use the code in /Car.lnk/Car.lnk.ino and load it on the esp module
- in this step, you should take note of the IP given to your esp module and enter it on the main.py code

## 3. install the app on your mobile phone
- go to this URL and download the app on your phone: <a href="https://play.google.com/store/apps/details?id=com.pas.webcam"> IpWebcam </a>
- run the app and enter the given IP in the main.py code (make sure your laptop, phone, and esp module are on the same network and the signal strength is good)

## 4. make a test environment
you should make a test environment and use it to change code parameters in order for the car to run smoothly. </br>
I made mine with black electrical tape and white paper.
</br>
<img src="images/test_env.png">

## 5. download and optimize the object detection model
I used an openvino model for my object detection model.
</br>
use the notebook in the utils directory to download and optimize the object detection model.
(for more information use the links in the references.)

## 6. change parameters and check the code
with the phone and esp IPs entered in the main.py code run it.</br>
it should show the picture from your phone with commands and debug texts </br>
adjust the high_tresh and low_tresh in the laneDetection class instance in order to change the window that the code uses to detect the lanes. (also adjust the black_treshold parameter based on the lighting and your lanes color. higher number means the wider range of brightness is used for detection)
</br>
run the code several times and change the parameters when the detection is solid go to the next step.

## 7. run the code
when all the parameters are set you can run the code and when you press space the car moves and changes direction.
</br>
this code can also detect cars and people as obstacles and stop signs

# results
here are some of the outputs of obstacle and lane detection results.
<img src="/videos/run1.gif">
</br>
<img src="images/turn_right.png">
</br>
<img src="images/car_detection.png">
</br>
<img src="images/person_detection.png">
</br>
<img src="images/stop_sign_detecion.png">



# references
- <a href="https://docs.openvino.ai/latest/notebooks/401-object-detection-with-output.html"> https://docs.openvino.ai/latest/notebooks/401-object-detection-with-output.html </a>
- N. S. a. I. M. M. a. A. N. M. a. R. S. A. a. S. W. H. M. a. D. A. M. Aminuddin, "A new approach to highway lane detection by using Hough transform technique," Journal of Information and Communication Technology, vol. 16, no. 2, pp. 244-260, 2017.
- <a href="https://randomnerdtutorials.com/esp8266-nodemcu-hc-sr04-ultrasonic-arduino"> https://randomnerdtutorials.com/esp8266-nodemcu-hc-sr04-ultrasonic-arduino </a>
- <a href="https://github.com/openvinotoolkit/open_model_zoo/tree/master/models/public/ssdlite_mobilenet_v2"> https://github.com/openvinotoolkit/open_model_zoo/tree/master/models/public/ssdlite_mobilenet_v2 </a>