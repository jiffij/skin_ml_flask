# import flask
import io
# import string
# import time
# import os
import numpy as np
import tensorflow as tf
from PIL import Image
from flask import Flask, jsonify, request

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
    # print(predict_result(img))

    return jsonify({'result': list(np.float64(predict_result(img)[0]))})
    

@app.route('/', methods=['GET'])
def index():
    return 'skin cancer classifier'


if __name__ == '__main__':
    app.run(debug=False, port=5000, host='0.0.0.0')