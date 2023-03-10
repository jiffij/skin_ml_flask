# import flask
import io
from threading import Thread
# import string
# import time
import os
import numpy as np
import tensorflow as tf
from PIL import Image
from flask import Flask, jsonify, request
import pandas as pd
from sklearn.utils import resample
from keras.utils.np_utils import to_categorical
import firebase_admin
from firebase_admin import credentials, firestore
import encryption
import json


cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

model = tf.keras.models.load_model('./assets/Xception_2.h5')
# df = pd.read_csv(os.path.join('..', 'input', 'aug_HAM10000_metadata.csv'))
# # Merging images from both folders HAM10000_images_part1.zip and HAM10000_im ages_part2.zip into one dictionary
# df_0 = df[df['label'] == 0]
# df_1 = df[df['label'] == 1]
# df_2 = df[df['label'] == 2]
# df_3 = df[df['label'] == 3]
# df_4 = df[df['label'] == 4]
# df_5 = df[df['label'] == 5]
# df_6 = df[df['label'] == 6]

# n_samples = 10
# df_0_balanced = resample(df_0, replace=True, n_samples=n_samples, random_state=42)
# df_1_balanced = resample(df_1, replace=True, n_samples=n_samples, random_state=42)
# df_2_balanced = resample(df_2, replace=True, n_samples=n_samples, random_state=42)
# df_3_balanced = resample(df_3, replace=True, n_samples=n_samples, random_state=42)
# df_4_balanced = resample(df_4, replace=True, n_samples=n_samples, random_state=42)
# df_5_balanced = resample(df_5, replace=True, n_samples=n_samples, random_state=42)
# df_6_balanced = resample(df_6, replace=True, n_samples=n_samples, random_state=42)

# df_balanced = pd.concat([df_0_balanced, df_1_balanced, df_2_balanced, df_3_balanced, df_4_balanced, df_5_balanced, df_6_balanced])
# df_balanced['image'] = df_balanced['path'].map(lambda x: np.asarray(Image.open(x).resize((75, 75))))
# X = np.asarray(df_balanced['image'].tolist())
# X = X/255.
# X = X.astype(np.float32)
# Y = df_balanced['label']
# Y = to_categorical(Y, num_classes=7)


def prepare_image(img):
    img = Image.open(io.BytesIO(img))
    img = img.resize((75, 75))
    img = np.array(img, dtype=np.float32)/255
    img = img.reshape(1, 75, 75, 3)
    return img


def predict_result(img):
    return model.predict(img)

# def train(img):
#     clone = tf.keras.models.clone_model(model)
#     clone.fit(img)
#     loss, accuracy = model.evaluate(X, Y, verbose=1)
#     clone_loss, clone_accuracy = clone.evaluate(X, Y, verbose=1)
#     if clone_accuracy > accuracy:
#         clone.save('./assets/Xception_2.h5')
#         model = clone
#     return 0

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
    # print(predict_result(img))
    
    # thread = Thread(target=train, kwargs={'value': request.args.get('img', img)})
    # thread.start()
    
    return jsonify({'result': list(np.float64(predict_result(img)[0]))})
    

@app.route('/publickey', methods=['GET'])
def index():
    return encryption.get_key('assets/rsa_public_key.pem', str_format=True)

@app.route('/add', methods=['POST'])
def create():
    """
        create() : Add document to Firestore collection with request body.
        Ensure you pass a custom ID as part of json body in post request,
        e.g. json={'id': '1', 'title': 'Write a blog post'}
    """
    print('running create')
    try:
        # path = request.json['path']
        # body = request.get_json()
        # del body['path']
        path = request.headers.get('path')
        body = request.get_data()
        print(body)
        body = json.loads(encryption.decrypt_data(body))
        print(body)
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
        print(client_key)
        if path:
            body = db.document(path).get()
            body = json.dumps(body.to_dict())
            body = encryption.encrypt_data_wth_client_key(body, client_key)
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
    app.run(debug=False, port=5000, host='0.0.0.0')