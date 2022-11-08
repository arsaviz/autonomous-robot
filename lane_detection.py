import cv2
import numpy as np

# this class is used to detect lane lines in an image
class LaneDetection:
    def __init__(self, low_tresh=50, high_tresh=150, black_treshold=100):
        self.black_treshold = black_treshold
        self.low_tresh = low_tresh
        self.high_tresh = high_tresh 

    def mask_black_tape(self, frame):
        frame = cv2.inRange(frame, (0, 0, 0), (self.black_treshold, self.black_treshold, self.black_treshold))
        return frame  

    def ROI_mask(self, image):
        
        height = image.shape[0]
        width = image.shape[1]

        polygons = np.array([ 
            [(0, height-self.low_tresh), (0, height - self.high_tresh), (width, height - self.high_tresh), (width-0, height-self.low_tresh)] 
            ]) 
        
        mask = np.zeros_like(image) 
        cv2.fillPoly(mask, polygons, 255) 

        masked_image = cv2.bitwise_and(image, mask)
        
        return masked_image

    def find_lane_centers(self, masked_image):
        width = masked_image.shape[1]
        height = masked_image.shape[0]
        white_pixels = cv2.findNonZero(masked_image)

        if white_pixels is None:
            return [0, height], [width, height]

        left_pixels = []
        right_pixels = []
        left_right_tresh = 40
        for pixel in white_pixels:
            if (pixel[0][0] - width/2) < left_right_tresh:
                left_pixels.append(pixel)
            if (pixel[0][0] - width/2) > left_right_tresh:
                right_pixels.append(pixel)

        left_avg = np.average(left_pixels, axis=0)
        right_avg = np.average(right_pixels, axis=0)
        if len(left_pixels) > 0:
            left_avg = left_avg[0]
        else:
            left_avg = [0, height]
        if len(right_pixels) > 0:
            right_avg = right_avg[0]
        else:
            right_avg = [0, height]

        return left_avg, right_avg



    def detect(self, frame):
        black_tape = self.mask_black_tape(frame)
        masked_image = self.ROI_mask(black_tape)
        left, right = self.find_lane_centers(masked_image)

        center_x = int((left[0] + right[0])/2)
        center_y = int((left[1] + right[1])/2)

        return center_x, center_y

    def debug_image(self, frame):
        black_tape = self.mask_black_tape(frame)
        masked_image = self.ROI_mask(black_tape)

        return black_tape, masked_image



                

                
