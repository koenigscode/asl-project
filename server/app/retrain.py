"""
File: retrain.py
Description: Source code which provides a function to retrain the model.

Contributors:
Parisa Babaei
Adam Faundez Laurokari

Created: 2024-12-26
Last Modified: 2025-01-02

Project: A Sign From Above
URL: https://git.chalmers.se/courses/dit826/2024/group4

License: MIT License (see LICENSE file for details)
"""

from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import EarlyStopping
from app.models import TrainingJob, TrainedModel
from dotenv import load_dotenv
from django.core.files import File
import keras
import numpy as np
import tempfile
import os
import sys

sys.path.insert(1, 'model_training/')
import data_prep as prep


# Retrain a model based on a training job
def retrain(job_id):
    # Constants
    DETECTOR_PATH = './models/hand_landmarker.task'
    JOB = TrainingJob.objects.get(id=job_id)
    NEW_NAME = JOB.name
    DATASET = JOB.dataset
    BASE_MODEL = JOB.base_model

    # Get base model info
    MODEL_PATH = BASE_MODEL.model_file.path
    BASE_MODEL_NAME = BASE_MODEL.name
    MODEL_SETTING = f'../models/{BASE_MODEL_NAME}.env'
    load_dotenv(MODEL_SETTING)
    NUM_FEATURES = int(os.getenv('NUM_FEATURES'))
    SELECT_WORDS = os.getenv('WORDS').split(',')
    FPS = float(os.getenv('FPS'))

    # Get dataset info
    DATASET_PATH = DATASET.root_directory

    # Load the base model
    model = keras.models.load_model(MODEL_PATH)

    # Load, pad, and split the dataset
    print("Loading dataset...")
    print(f"Selected words: {SELECT_WORDS}")
    print(f"Dataset path: {DATASET_PATH}")
    print(f"Detector path: {DETECTOR_PATH}")
    print(f"Base model: {BASE_MODEL_NAME}")
    X, y, num_videos, highest_frame, bad_videos = prep.get_data(SELECT_WORDS, DATASET_PATH, DETECTOR_PATH)
    padded_X, mask = prep.padX(X, num_videos, highest_frame, NUM_FEATURES)
    if num_videos < 2:
        X_train, y_train = padded_X, y
        X_test, y_test = [[[]]], []
    else:
        X_train, X_test, y_train, y_test = train_test_split(padded_X, y, test_size=0.2, random_state=42)
    X_train = np.array(X_train)
    X_test = np.array(X_test)
    y_train = np.array(y_train)
    y_test = np.array(y_test)

    # Retrain the model
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    early_stopping = EarlyStopping(monitor='loss', patience=3, restore_best_weights=True)
    model.fit(X_train, y_train, epochs=100, callbacks=[early_stopping])

    # Evaluate the model
    if num_videos < 2:
        test_loss, test_accuracy = 0.0,0.0
        word_accuracy = {}
    else:
        test_loss, test_accuracy = model.evaluate(X_test, y_test)
        word_accuracy = prep.get_word_accuracy(SELECT_WORDS, model, X_test, y_test)

    # Save the model
    with tempfile.TemporaryDirectory() as temp_dir:
        model.save(f"{temp_dir}/{NEW_NAME}.keras")
        trained_model = TrainedModel(name=NEW_NAME, max_frames=highest_frame, num_features=NUM_FEATURES, accuracy=test_accuracy, words=','.join(SELECT_WORDS), fps=FPS, word_accuracy=word_accuracy)
        trained_model.model_file.save(f"{NEW_NAME}.keras", File(open(f"{temp_dir}/{NEW_NAME}.keras", 'rb')))
        trained_model.save()

    # Save the model settings
    with open(f"./models/{NEW_NAME}.env", "w") as file:
        file.write(f"MAX_FRAMES={highest_frame}\n")
        file.write(f"NUM_FEATURES={NUM_FEATURES}\n")
        file.write(f"WORDS={','.join(SELECT_WORDS)}\n")
        file.write(f"FPS={FPS}\n")
        file.write(f"TEST_ACC={test_accuracy}\n")
        file.write(f'WORD_ACC="{word_accuracy}"\n')

    return trained_model
