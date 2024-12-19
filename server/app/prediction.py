import os
from stopwatch import Stopwatch
import subprocess
import hashlib
import shutil
import tensorflow as tf
from tensorflow import keras
from keras.models import load_model
from . import landmark_detector as ld
import numpy as np
import cv2
import logging
from dotenv import load_dotenv

MODEL_NAME = os.getenv('MODEL_NAME')
if MODEL_NAME is None:
    raise ValueError("Environment variable 'MODEL_NAME' is not set.")

DETECTOR_PATH = '/models/hand_landmarker.task'
MODEL_PATH = f'/models/{MODEL_NAME}.keras'
MODEL_SETTINGS = f'/models/{MODEL_NAME}.env'
load_dotenv(MODEL_SETTINGS)


NUM_FEATURES = os.getenv('NUM_FEATURES')
if NUM_FEATURES is None:
    raise ValueError("Environment variable 'NUM_FEATURES' is not set.")
num_features = int(NUM_FEATURES)

MAX_FRAMES = os.getenv('MAX_FRAMES')
if MAX_FRAMES is None:
    raise ValueError("Environment variable 'MAX_FRAMES' is not set.")
max_frames = int(MAX_FRAMES)

WORDS = os.getenv('WORDS')
if WORDS is None:
    raise ValueError("Environment variable 'WORDS' is not set.")
words = WORDS.split(',')

FPS = os.getenv('FPS')
if FPS is None:
    raise ValueError("Environment variable 'FPS' is not set.")
fps = int(FPS)

model = load_model(MODEL_PATH)
detector = ld.get_detector(DETECTOR_PATH)

logger = logging.getLogger('asl')


def preprocess_video(video_path, target_fps=5):
    file_name,  _ = os.path.splitext(video_path)
    output_path = f"{file_name}_reencoded.mp4"
    sw = Stopwatch(2)
    subprocess.run(
        ["ffmpeg", "-i", video_path, "-c:v", "mjpeg", "-q:v", "5", "-r", str(target_fps), output_path],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    sw.stop()
    logger.info(f"FFmpeg reencoding completed in {sw.duration} seconds")

    return output_path


def generate_random_hash(length=10):
    return hashlib.sha256(os.urandom(16)).hexdigest()[:length]

def save_recording(video_path, correct_class):
    destination_dir = f'/recordings/{correct_class}'
    os.makedirs(destination_dir, exist_ok=True)

    file_extension = os.path.splitext(video_path)[1]
    random_filename = f"{generate_random_hash()}{file_extension}"
    destination = os.path.join(destination_dir, random_filename)

    shutil.copy(video_path, destination)
    logger.info(f"Saved recording to {destination}")
    return destination


def predict(video_path, correct_class):
    video_X = []
    video_path = preprocess_video(video_path)
    sw = Stopwatch(2)
    landmarks = ld.get_landmarks(video_path, detector)
    sw.stop()
    logger.info(f"Landmark detection completed in {sw.duration} seconds")

    prediction_X = []

    if len(landmarks) == 0:
        logger.info("No landmarks detected")
        if os.getenv("SAVE_RECORDINGS") != "True":
            logger.info("Not saving video because no landmarks were detected")
        return None
    else:
        for frame in range(len(landmarks)):
            features = np.array(landmarks[frame]).flatten()
            features = np.pad(
                features, (0, num_features - len(features)), 'constant')
            video_X.append(features)
        for i in range(max_frames-len(video_X)):
            temp = np.zeros((num_features))
            video_X.append(temp)

    prediction_X.append(video_X)

    # copy video to /recordings
    if os.getenv("SAVE_RECORDINGS") == "True":
        save_recording(video_path, correct_class)
        logger.info(f"Saved video to /recordings/{correct_class}/")

    sw.reset()
    sw.start()
    predictions = model.predict(np.array(prediction_X), verbose=0)
    sw.stop()
    logger.info(f"Prediction completed in {sw.duration} seconds")

    predicted_class = np.argmax(predictions)
    # Returns the maximum probability
    predicted_probability = np.max(predictions)

    logger.info("--------------------")
    logger.info("Probabilities for each word:")
    for i, prob in enumerate(predictions[0]):
        logger.info(f"{words[i]}: {prob:.3f}")

    logger.info(f"predicted {words[predicted_class]}"
                + f" with probability {predicted_probability}")
    logger.info("--------------------")

    logger.info(f"User was supposed to sign: \"{correct_class}\", and it was recognized as: \"{words[predicted_class]}\"")

    return (words[predicted_class], predicted_probability)
