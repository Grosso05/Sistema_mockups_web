# calculate.py
import cv2
import numpy as np

def get_white_presence(image_path):
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresholded = cv2.threshold(gray_image, 240, 255, cv2.THRESH_BINARY)
    white_percentage = (np.sum(thresholded == 255) / thresholded.size) * 100
    print(f"El color blanco se encuentra en un : {white_percentage:.2f}%")
    return white_percentage
