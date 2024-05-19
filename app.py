from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, messaging
import imgbbpy
import base64
import os
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image

app = Flask(__name__)

load_dotenv()

# Initialize Firebase Admin SDK
cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred)

client = imgbbpy.SyncClient(os.getenv('IMGBB_API_KEY'))

def send_push(title, msg, frame_url):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=msg
        ),
        android=messaging.AndroidConfig(
            notification=messaging.AndroidNotification(
                image=frame_url
            )
        ),
        topic='fire-alert'
    )
    response = messaging.send(message)
    print('Successfully sent message:', response)

@app.route('/send-alert', methods=['POST'])
def send_alert():
    data = request.json
    image_data = data.get('image_data')
    if not image_data:
        return jsonify({"error": "No image data provided"}), 400

    # Decode the base64 image
    image = Image.open(BytesIO(base64.b64decode(image_data)))
    image_path = "frame0.jpg"
    image.save(image_path)

    # Upload the image to imgbb
    response = client.upload(file=image_path)
    frame_url = response.url

    # Send push notification
    send_push("FIRE ALERT 🔥🔥", "Fire detected in the CCTV camera", frame_url)
    return jsonify({"status": "Alert sent", "frame_url": frame_url}), 200

if __name__ == '__main__':
    app.run(debug=True)
