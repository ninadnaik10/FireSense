import base64
import json
from ultralytics import YOLO
import cvzone
import cv2
from pyfcm import FCMNotification as fcm
import firebase_admin
from firebase_admin import credentials, messaging
import math
import imgbbpy
import os
from dotenv import load_dotenv

load_dotenv()

import requests

client = imgbbpy.SyncClient(os.getenv('IMGBB_API_KEY'))


cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred)

count = 0

def sendPush(title, msg, frame,dataObject=None):
    # See documentation on defining a message payload.
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=msg
        ),
        android=messaging.AndroidConfig(
            notification=messaging.AndroidNotification(
                image=frame
            )
        ),
        topic='fire-alert'
    )
    response = messaging.send(message)
    print('Successfully sent message:', response)


cap = cv2.VideoCapture(0)
model = YOLO('best2.pt')
classnames = ['fire']

while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, (640, 480))
    retval, buffer = cv2.imencode('.jpg', frame)
    jpg_as_text = base64.b64encode(buffer)
    result = model(frame, stream=True)

    # Getting bbox,confidence and class names information to work with
    for info in result:
        boxes = info.boxes
        for box in boxes:
            confidence = box.conf[0]
            confidence = math.ceil(confidence * 100)
            Class = int(box.cls[0])

            if confidence > 97:
                count+=1
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 5)
                cvzone.putTextRect(frame, f'{classnames[Class]} {confidence}%', [x1 + 8, y1 + 100],
                                   scale=1.5, thickness=2)
            if count==5:
                name = "frame0.jpg"
                cv2.imwrite(name, frame) 
                print('image saved')
                response = client.upload(file=name)
                print(response)
                sendPush("FIRE ALERT 🔥🔥", "Fire detected in the CCTV camera",frame=response.url)
                print('notification sent')
                count=0
                
    cv2.imshow('frame', frame)
    cv2.waitKey(1)