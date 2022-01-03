from numpy import expand_dims, squeeze, asarray
from keras_facenet import FaceNet 
import tensorflow as tf
import tensorflow_hub as hub
import os
import sys
from os.path import join
from mtcnn.mtcnn import MTCNN
from PIL import Image

import requests
import tempfile

embedder = FaceNet()
module_handle = "https://tfhub.dev/google/imagenet/mobilenet_v2_140_224/feature_vector/4"
module = hub.load(module_handle)

def saveImage(url):
    new_file, filename = tempfile.mkstemp(suffix="jpg")
    with os.fdopen(new_file, 'wb') as tmp:
        response = requests.get(url, stream=True)

        if not response.ok:
            print("Error")
            return None

        for block in response.iter_content(1024):
            if not block:
                break
            tmp.write(block)
    return filename

def load_img_pixels(filename):
    # load image from file
    image = Image.open(filename)
    # convert to RGB, if needed
    image = image.convert('RGB')
    # convert to array
    pixels = asarray(image)
    return pixels

def extract_img_face_analysis(pixels):
    # create the detector, using default weights
    detector = MTCNN()
    # detect faces in the image
    results = detector.detect_faces(pixels)
    return results

def extract_faces(pixels, facebox, required_size=(160, 160)):
    # extract the bounding box
    x1, y1, width, height = facebox
    x1, y1 = abs(x1), abs(y1)
    x2, y2 = x1 + width, y1 + height
    # extract the face
    face = pixels[y1:y2, x1:x2]
    img = Image.fromarray(face)
    img = img.resize(required_size)
    return asarray(img)

def get_embedding(face_pixels):
    # scale pixel values
    face_pixels = face_pixels.astype('float32')
    # standardize pixel values across channels (global)
    mean, std = face_pixels.mean(), face_pixels.std()
    face_pixels = (face_pixels - mean) / std
    # transform face into one sample
    samples = expand_dims(face_pixels, axis=0)
    # make prediction to get embedding
    yhat = embedder.embeddings(samples)
    return yhat[0]

def modelFaceAnalysis(filename):
    return embedder.extract(filename, threshold=0.80)

def load_img(path):
    # Reads the image file and returns data type of string
    img = tf.io.read_file(path)
    # Decodes the image to W x H x 3 shape tensor with type of uint8
    img = tf.io.decode_jpeg(img, channels=3)
    # Resizes the image to 224 x 224 x 3 shape tensor
    img = tf.image.resize_with_pad(img, 224, 224)
    # Converts the data type of uint8 to float32 by adding a new axis
    # img becomes 1 x 224 x 224 x 3 tensor with data type of float32
    # This is required for the mobilenet model we are using
    img = tf.image.convert_image_dtype(img,tf.float32)[tf.newaxis, ...]
    return img

def get_image_feature_vectors(filename):
    img = load_img(filename)
    features = module(img)
    feature_set = squeeze(features)
    return feature_set.tolist()

def featureAndFaceEmbedding(payload):
    url = payload["payload"]["url"]
    filename = saveImage(url)
    feature = get_image_feature_vectors(filename)
    faceEmbedding = modelFaceAnalysis(filename)
    return {
        "feature": feature,
        "faceEmbedding": faceEmbedding
    }

def faceEmbedding(payload):
    url = payload["payload"]["url"]
    filename = saveImage(url)
    faceEmbedding = modelFaceAnalysis(filename)
    return {
        "faceEmbedding": faceEmbedding
    }

def featureEmbedding(payload):
    url = payload["payload"]["url"]
    filename = saveImage(url)
    feature = get_image_feature_vectors(filename)
    return {
        "feature": feature,
    }