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
        body = json.loads(rsa.decrypt_data(body))
        # print(body)
        body = aes_cipher.encrypt_json(body)
        # print(body)
        db.document(path).set(body)# request.json
        return jsonify({"success": True}), 200
    except Exception as e:
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

# @app.route('/update', methods=['POST', 'PUT'])
# def update():
#     """
#         update() : Update document in Firestore collection with request body.
#         Ensure you pass a custom ID as part of json body in post request,
#         e.g. json={'id': '1', 'title': 'Write a blog post today'}
#     """
#     try:
#         id = request.json['id']
#         todo_ref.document(id).update(request.json)
#         return jsonify({"success": True}), 200
#     except Exception as e:
#         return f"An Error Occurred: {e}"

# @app.route('/delete', methods=['GET', 'DELETE'])
# def delete():
#     """
#         delete() : Delete a document from Firestore collection.
#     """
#     try:
#         # Check for ID in URL query
#         todo_id = request.args.get('id')
#         todo_ref.document(todo_id).delete()
#         return jsonify({"success": True}), 200
#     except Exception as e:
#         return f"An Error Occurred: {e}"
    
#     return

if __name__ == '__main__':
    app.run(debug=False, port=5000, host='0.0.0.0', threaded = True)