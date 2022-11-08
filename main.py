from camera import Camera
from car import Car
from lane_detection import LaneDetection
from object_detection import ObjectDetection
from datetime import datetime, timedelta

import cv2

### change these values to match your setup
cam = Camera("192.168.77.139", width=800, height=480, quality=70)
car = Car("192.168.77.218")
###

### this value is the percentage of the speed the car motors will run at
speed = 90
car.set_speed(speed)
### adjust these values for the lane detection
ld = LaneDetection(black_treshold=100 , low_tresh=50, high_tresh=90)
od = ObjectDetection()

cap = cv2.VideoCapture(cam.feed)
fps = 0
start_time = 0
end_time = 0
stop_sign_detected_time = datetime.now() - timedelta(seconds=3)
obstacle_detected = False

i = 0

car_control = False

# change this value to change how the car changes direction
# the higher the value, the more the car will turn
center_tresh = 40
sleep_time = 0.04 * 1

control = 'stop'

boxes = []
objects = []

fourcc = cv2.VideoWriter_fourcc(*"MJPG")
out = cv2.VideoWriter('output_' + str(datetime.now().strftime("%Y%m%d_%H%M%S")) + '.avi', fourcc, 20.0, (cam.width, cam.height))

while True:
   # resume movement if no obstacle is detected
   if obstacle_detected and control == 'obstacle':
      print('obstacle removed, resume movement')
      control = 'stop'
      car.stop()
      car_control = True
      obstacle_detected = False

   # resume movement five seconds after reaching stop signs
   if control == 'stop-sign':
      time_diff = datetime.now() - stop_sign_detected_time
      if time_diff.seconds > 5:
         print('stopped for 5 seconds, resume movement')
         control = 'stop'
         car.stop()
         car_control = True
         stop_sign_detected_time = datetime.now()

   

   i += 1
   ret, frame = cap.read()

   start_time = cv2.getTickCount()

   width = frame.shape[1]
   height = frame.shape[0]

   # detect objects every other 3 frames
   if i % 3 == 0:
      _, objects, boxes = od.detect(frame)
   if boxes != []:
      frame = od.draw_boxes(frame, boxes)

   # check for obstacles and stop signs
   for label, score, box in objects:
      if label == "car":
         x1, y1, x2, y2 = box[0], box[1], box[0] + box[2], box[1] + box[3]
         car_width = x2 - x1
         car_height = y2 - y1
         width_ratio = car_width / width
         if width_ratio > 0.40 and control != 'obstacle':
            print("car obstacle")
            obstacle_detected = True
            car_control = False
            control = 'obstacle'
            car.stop()

      if label == "person":
         x1, y1, x2, y2 = box[0], box[1], box[0] + box[2], box[1] + box[3]
         person_width = x2 - x1
         person_height = y2 - y1
         width_ratio = person_width / width
         if width_ratio > 0.08 and control != 'obstacle':
            print("person_obstacle")
            obstacle_detected = True
            car_control = False
            control = 'obstacle'
            car.stop()

      if label == "stop sign":
         x1, y1, x2, y2 = box[0], box[1], box[0] + box[2], box[1] + box[3]
         stop_width = x2 - x1
         stop_height = y2 - y1
         width_ratio = stop_width / width
         if width_ratio > 0.05 and control != 'stop-sign':
            time_diff = datetime.now() - stop_sign_detected_time
            if time_diff.seconds > 2:
               print('stop sign obstacle')
               car_control = False
               stop_sign_detected_time = datetime.now()
               control = 'stop-sign'
               car.stop()

   
   
   # display center line on frame
   center_x, center_y = ld.detect(frame)
   cv2.circle(frame, (int(width/2), center_y), 10, (0,255, 0), -1)
   cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)

   # control car
   if center_x - int(width/2) > center_tresh:
      cv2.putText(frame, "Turn Right", (int(width/2), int(height- 50)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
      if car_control:
         if control != 'right':
            car.right()
            control = 'right'
   elif center_x - int(width/2) < -center_tresh:
      cv2.putText(frame, "Turn Left", (int(width/2), int(height- 50)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
      if car_control:
         if control != 'left':
            car.left()
            control = 'left'
   else:
      cv2.putText(frame, "Straight", (int(width/2), int(height- 50)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
      if car_control:
         if control != 'forward':
            car.forward()
            control = 'forward'

   # display obstacle and stop signs warnings
   if control == 'obstacle':
      cv2.putText(frame, "OBSTACLE DETECTED", (int(width/2) - 320, int(height/2)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
   if control == 'stop-sign':
      cv2.putText(frame, "STOP SIGN DETECTED", (int(width/2) - 320, int(height/2)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
      count_down = 5 - (datetime.now() - stop_sign_detected_time).seconds
      cv2.putText(frame, "Resuming in: " + str(count_down), (int(width/2) - 320, int(height/2) + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

   # calculate and display fps count
   end_time = cv2.getTickCount()
   fps = cv2.getTickFrequency() / (end_time - start_time)
   cv2.putText(frame, "FPS: " + str(int(fps)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

   # display lanes on frame
   lanes_sillouette = ld.debug_image(frame)[1]
   lanes_sillouette = cv2.cvtColor(lanes_sillouette, cv2.COLOR_GRAY2BGR)
   cv2.imshow("lanes_sillouette", lanes_sillouette)
   cv2.addWeighted(lanes_sillouette, 0.5, frame, 1, 0, frame)

   cv2.imshow("frame", frame)
   # uncomment to save video
   # out.write(frame)

   key = cv2.waitKey(1) & 0xFF
   if key == ord('q'):
      car.stop()
      break
   if key == ord(' '):
      car_control = not car_control
      print(f"Car control: {car_control}")
      car.stop()
      control = 'stop'

   # for debugging the car speed during execution
   if key == ord('w'):
      speed += 1
      car.set_speed(speed)
      print(f"Speed: {speed}")
   if key == ord('s'):
      speed -= 1
      car.set_speed(speed)
      print(f"Speed: {speed}")





