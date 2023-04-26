import io
from threading import Thread
import os
import numpy as np
import tensorflow as tf
from PIL import Image
from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore
import rsa
import json
from aes import AESCipher
import base64
from io import BytesIO
import jwt
import datetime
import time



cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

aes_cipher = AESCipher('HealthCare')

model = tf.keras.models.load_model('./assets/Xception_2.h5')

def prepare_image(img):
    img = Image.open(io.BytesIO(img))
    img = img.resize((75, 75))
    img = np.array(img, dtype=np.float32)/255
    img = img.reshape(1, 75, 75, 3)
    return img


def predict_result(img):
    return model.predict(img)

def generateVideoCallToken(paritipantName, roomName, expiredDate, notBefore):
    payload = {
    "exp": expiredDate,             # expired datetime (numeric date)
    "iss": "APIFewQrMg9Atkj",       # api key
    "nbf": notBefore,               # not valid before a dateTime (numeric date)
    "sub": paritipantName,          # participant display name
    "video": {
        "canPublish": True,
        "canPublishData": True,
        "canSubscribe": True,
        "room": roomName,           # room name: As each roomName in Dr.UST should be unique, using appoinmentID as roomName is recommanded
        "roomJoin": True
    }
    }
    secret = "jyzXP5dAXKKudHZaK8ut5fJRjclelHeSpMBeIcj6HieE"     # secret key

    encoded_jwt = jwt.encode(payload, secret, algorithm="HS256")
    return encoded_jwt

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def infer_image():
    if 'file' not in request.files:
        return "Please try again. The Image doesn't exist"
    file = request.files.get('file')
    if not file:
        return
    img_bytes = file.read()
    img = prepare_image(img_bytes)
    
    return jsonify({'result': list(np.float64(predict_result(img)[0]))})


@app.route('/predictEncrypt', methods=['POST']) # TODO
def predict_encrypted():
    body = request.get_data()
    body = rsa.decrypt_data_Byte(body)
    image = Image.open(BytesIO(body))
    image.show()
    img = prepare_image(body)
    print(predict_result(img)[0])
    return jsonify({'result': list(np.float64(predict_result(img)[0]))})
    

@app.route('/publickey', methods=['GET'])
def index():
    return rsa.get_key('assets/rsa_public_key.pem', str_format=True)


@app.route('/add', methods=['POST'])
def create():
    """
        create() : Add document to Firestore collection with request body.
        Ensure you pass a custom ID as part of json body in post request,
        e.g. json={'id': '1', 'title': 'Write a blog post'}
    """
    # print('running create')
    try:
        path = request.headers.get('path')
        body = request.get_data()
        # print(body)
        # body = json.loads(rsa.decrypt_data(body))
        body = json.loads(rsa.decrypt_data((body).decode('utf-8')))
        # print(body)
        body = aes_cipher.encrypt_json(body)
        # print(body)
        db.document(path).update(body)# request.json
        return jsonify({"success": True}), 200
    except Exception as e:
        print(e)
        return f"An Error Occurred: {e}"


@app.route('/set', methods=['POST'])
def set_doc():
    """
        create() : Add document to Firestore collection with request body.
        Ensure you pass a custom ID as part of json body in post request,
        e.g. json={'id': '1', 'title': 'Write a blog post'}
    """
    # print('running create')
    print("set")
    try:
        path = request.headers.get('path')
        body = request.get_data()
        # print(body)
        body = json.loads(rsa.decrypt_data((body).decode('utf-8')))
        # print(body)
        body = aes_cipher.encrypt_json(body)
        # print(body)
        db.document(path).set(body)# request.json
        return jsonify({"success": True}), 200
    except Exception as e:
        print(e)
        return f"An Error Occurred: {e}"



@app.route('/list', methods=['POST'])
def read():
    """
        read() : Fetches documents from Firestore collection as JSON.
        todo : Return document that matches query ID.
        all_todos : Return all documents.
    """
    try:
        # Check if ID was passed to URL query
        path = request.headers.get('path')
        client_key = request.get_data()
        # print(client_key)
        if path:
            body = db.document(path).get()
            # print(type(body.to_dict()))
            body = aes_cipher.decrypt_json(body.to_dict())
            # print(body)
            body = json.dumps(body)
            # print("here")
            body = rsa.encrypt_data_wth_client_key(body, client_key.decode())
            return body, 200
            # return jsonify(body.to_dict()), 200
        # else:
        #     all_body = [doc.to_dict() for doc in db.stream()]
        #     return jsonify(all_body), 200
    except Exception as e:
        return f"An Error Occurred: {e}", 204
    
@app.route('/videocall', methods=['POST'])
def tokengen():
    # body = request.get_data()
    # print(body)
    # body = json.loads(rsa.decrypt_data(body))
    name = request.headers.get('name')
    roomName = request.headers.get('roomName')
    client_key = request.get_data()
    
    # now = datetime.datetime.utcnow()
    # timestamp = int(time.mktime(now.timetuple()))
    # numeric_date = timestamp + (now.microsecond / 1000000)
    # future_time = now + datetime.timedelta(minutes=30)
    # future_timestamp = int(time.mktime(future_time.timetuple()))
    # numeric_date_future = future_timestamp + (future_time.microsecond / 1000000)
    n = int(time.time())
    f = n +30*60
    token = generateVideoCallToken(name, roomName, f, n)
    
    # client_key = body['client_key']
    print(token)
    token = rsa.encrypt_data_wth_client_key(token, client_key)
    return token


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0', threaded = True)