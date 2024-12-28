from sklearn.model_selection import train_test_split
import keras
from tensorflow.keras.callbacks import EarlyStopping
from app.models import TrainingJob, Dataset, TrainedModel, models
from app.shared_state import get_event
from dotenv import load_dotenv
from django.core.files import File
import numpy as np
import tempfile
import os
import sys
sys.path.insert(1, 'model_training/')
import data_prep as prep


def retrain(job_id):
    detector_path = './models/hand_landmarker.task'
    job = TrainingJob.objects.get(id=job_id)
    new_name = job.name
    dataset = job.dataset
    base_model = job.base_model
    hyperparameters = job.hyperparameters

    # Get base model info
    model_path = base_model.model_file.path
    base_model_name = base_model.name
    model_setting = f'../models/{base_model_name}.env'
    load_dotenv(model_setting)
    num_features = int(os.getenv('NUM_FEATURES'))
    select_words = os.getenv('WORDS').split(',')
    fps = int(os.getenv('FPS'))

    # Get dataset info
    dataset_path = dataset.root_directory

    # Load the base model
    model = keras.models.load_model(model_path)

    # Load, pad, and split the dataset
    X, y, num_videos, highest_frame, bad_videos = prep.get_data(select_words, dataset_path, detector_path)
    padded_X, mask = prep.padX(X, num_videos, highest_frame, num_features)
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
    test_loss, test_accuracy = model.evaluate(X_test, y_test)
    word_accuracy = prep.get_word_accuracy(select_words, model, X_test, y_test)

    # Save the model
    with tempfile.TemporaryDirectory() as temp_dir:
        model.save(f"{temp_dir}/{new_name}.keras")
        trained_model = TrainedModel(name=new_name)
        trained_model.model_file.save(f"{new_name}.keras", File(open(f"{temp_dir}/{new_name}.keras", 'rb')))
        trained_model.save()

    with open(f"./models/{new_name}.env", "w") as file:
        file.write(f"MAX_FRAMES={highest_frame}\n")
        file.write(f"NUM_FEATURES={num_features}\n")
        file.write(f"WORDS={','.join(select_words)}\n")
        file.write(f"FPS={fps}\n")
        file.write(f"TEST_ACC={test_accuracy}\n")
        file.write(f'WORD_ACC="{word_accuracy}"\n')

    return trained_model