import os
import tensorflow as tf
from tensorflow import keras
from keras.models import load_model
from . import landmark_detector as ld
import numpy as np
import cv2
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'draft_model.keras')
DETECTOR_PATH = os.path.join(BASE_DIR, 'hand_landmarker.task')
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

    out = cv2.VideoWriter(video_path, -1, new_fps,
                          (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                           int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

    frame_index = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_index % (original_fps // new_fps) == 0:
            out.write(frame)
        frame_index += 1

    cap.release()
    out.release()


def predict(video_path):
    video_X = []
    adjust_video_fps(video_path)
    landmarks = ld.get_landmarks(video_path, detector)

    prediction_X = []

    if len(landmarks) == 0:
        logger.debug("No landmarks detected")
        return None
    else:
        logger.debug(f"detected {len(landmarks)} landmark frames")
        for frame in range(len(landmarks)):
            features = np.array(landmarks[frame]).flatten()
            features = np.pad(
                features, (0, num_features - len(features)), 'constant')
            video_X.append(features)
        for i in range(max_frames-len(video_X)):
            temp = np.zeros((num_features))
            video_X.append(temp)

    prediction_X.append(video_X)

    logger.debug(f"Shape of prediction_X: {np.array(prediction_X).shape}")
    predictions = model.predict(np.array(prediction_X), verbose=0)

    predicted_class = np.argmax(predictions)
    # Returns the maximum probability
    predicted_probability = np.max(predictions)

    logger.debug("Probabilities for each word:")
    for i, prob in enumerate(predictions[0]):
        logger.debug(f"{words[i]}: {prob:.3f}")

    logger.debug(f"predicted {words[predicted_class]}"
          + f" with probability {predicted_probability}")

    return (words[predicted_class], predicted_probability)
