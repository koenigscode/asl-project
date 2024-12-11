import os
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


def adjust_video_fps(video_path, target_fps=5):
    cap = cv2.VideoCapture(video_path)

    original_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if total_frames > max_frames:
        # dont exceed max frames
        new_fps = total_frames / max_frames
    else:
        new_fps = target_fps

    logger.info(f"Changed video to {new_fps} fps")

    temp_video_path = f"{os.path.splitext(video_path)[0]}_temp.mp4"
    out = cv2.VideoWriter(
        temp_video_path,
        cv2.VideoWriter_fourcc(*'mp4v'),
        new_fps,
        (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
         int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    )

    frame_index = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_index % (original_fps // new_fps) == 0:
            out.write(frame)
        frame_index += 1

    os.replace(temp_video_path, video_path)

    cap.release()
    out.release()


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
    adjust_video_fps(video_path, fps)
    landmarks = ld.get_landmarks(video_path, detector)

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

    predictions = model.predict(np.array(prediction_X), verbose=0)

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

    return (words[predicted_class], predicted_probability)
