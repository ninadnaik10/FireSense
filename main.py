import base64
import json
from ultralytics import YOLO
import cvzone
import cv2
import math
import requests
import os
from dotenv import load_dotenv

load_dotenv()

count = 0

cap = cv2.VideoCapture(0)
model = YOLO('best2.pt')
classnames = ['fire']

while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, (640, 480))
    retval, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    result = model(frame, stream=True)

    for info in result:
        boxes = info.boxes
        for box in boxes:
            confidence = box.conf[0]
            confidence = math.ceil(confidence * 100)
            Class = int(box.cls[0])

            if confidence > 97:
                count += 1
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 5)
                cvzone.putTextRect(frame, f'{classnames[Class]} {confidence}%', [x1 + 8, y1 + 100],
                                   scale=1.5, thickness=2)
            if count == 5:
                print('image ready to be sent')
                response = requests.post('http://localhost:5000/send-alert', json={'image_data': jpg_as_text})
                print('notification sent:', response.json())
                count = 0

    cv2.imshow('frame', frame)
    cv2.waitKey(1)
