import flask
import io
import string
import time
import os
import numpy as np
import tensorflow as tf
from PIL import Image
from flask import Flask, jsonify, request

model = tf.keras.models.load_model('./assets/Xception_2.h5')
img = Image.open('/home/jiff/Desktop/health_care/assets/ISIC_0024306.jpg')
img = img.resize((75, 75))
img = np.array(img, dtype=np.float32)/255
img = img.reshape(1, 75, 75, 3)

print(type( model.predict(img)[0]))