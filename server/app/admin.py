import shutil
from django.contrib import admin
from .models import Dataset, TrainingJob, TrainedModel
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
import zipfile
import os
from threading import Thread
from django.db import transaction
from django.conf import settings
from .utils import validate_dataset_structure
from .testTraining import testTraining
from .shared_state import get_event, clear_event
import mediapipe as mp
import numpy as np
import cv2 as cv
import keras
#from sklearn.model_selection import train_test_split
from keras import layers
from mediapipe.framework.formats import landmark_pb2
#from tqdm.notebook import tqdm
import random

#Global variables
MAX_EXTRACT_SIZE = 10000000000
current_training_thread = None

#Models

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('name', 'uploaded_at')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        zip_path = obj.data_file.path
        extract_to = os.path.join(settings.MEDIA_ROOT, 'datasets', obj.name)

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Security: Check for path traversal
                for member in zip_ref.namelist():
                    member_path = os.path.join(extract_to, member)
                    abs_member_path = os.path.abspath(member_path)
                    if not abs_member_path.startswith(os.path.abspath(extract_to)):
                        raise Exception("Attempted Path Traversal in ZIP File")

                # Security: Check for ZIP bombs
                total_size = sum([zinfo.file_size for zinfo in zip_ref.infolist()])
                if total_size > MAX_EXTRACT_SIZE:
                    raise Exception("Extracted content exceeds the maximum allowed size. size:" + str(total_size))

                zip_ref.extractall(extract_to)
        except Exception as e:
            messages.set_level(request, messages.ERROR)
            self.message_user(request, str(e), level=messages.ERROR)
            obj.delete()
            shutil.rmtree(extract_to, ignore_errors=True)
            return

        # Validate the dataset structure
        is_valid, message = validate_dataset_structure(extract_to)
        if not is_valid:
            # **Delete the uploaded ZIP file**
            obj.data_file.delete(save=False)
            # Delete the Dataset object from the database
            obj.delete()
            # Remove the extracted files
            shutil.rmtree(extract_to, ignore_errors=True)
            # Display error message
            messages.set_level(request, messages.ERROR)
            self.message_user(request, message, level=messages.ERROR)
            return

        # If validation passes
        messages.set_level(request, messages.SUCCESS)
        self.message_user(request, 'Dataset uploaded and extracted successfully.', level=messages.SUCCESS)


@admin.register(TrainingJob)
class TrainingJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'dataset', 'status', 'started_at', 'completed_at')
    list_filter = ('status',)
    search_fields = ('id', 'dataset__name')
    readonly_fields = ('started_at', 'completed_at')

    # Customize the form for adding/editing TrainingJob
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            if obj.status != 'PENDING':
                return  ('dataset', 'base_model', 'hyperparameters',  'status', 'output_model' ) + self.readonly_fields
        return self.readonly_fields

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('start/<int:job_id>/', self.admin_site.admin_view(self.start_job), name='trainingjob-start'),
            path('stop/<int:job_id>/', self.admin_site.admin_view(self.stop_job), name='trainingjob-stop')
        ]
        return custom_urls + urls

    def start_job(self, request, job_id):
        try:
            global current_training_thread

            # Here we get the TrainingJob object as a variable and change its status to 'IN_PROGRESS'
            job = TrainingJob.objects.get(id=job_id)
            job.status = 'IN_PROGRESS'
            job.save()

            if current_training_thread is None:
                # Start the training job in a separate thread
                get_event(job_id) # Create a stop event for the job
                current_training_thread = Thread(target=self._train_model_in_background, args=(job_id,))
                current_training_thread.start()
                self.message_user(request, "Training job started in background.", level=messages.SUCCESS)
            else:
                self.message_user(request, "Another training job is currently running. Cannot start another.", level=messages.WARNING)
                return redirect('/admin/myapp/trainingjob/')

        except Exception as e:
            job.status = 'ERROR'
            job.save()
            self.message_user(request, str("An error occured, error message: " + e), level=messages.ERROR)

        return redirect('/admin/myapp/trainingjob/')  # Redirect back to the change list
    
    def stop_job(self, request, job_id):
        """Stop the job by setting the stop flag and returning to PENDING."""
        try:
            global current_training_thread

            job = TrainingJob.objects.get(id=job_id)

            if job.status != 'IN_PROGRESS':
                self.message_user(request, "The job is not currently running.", level=messages.WARNING)
                return redirect('/admin/myapp/trainingjob/')

            # Wait for the training thread to stop
            if current_training_thread is not None and current_training_thread.is_alive():
                    get_event(job_id).set() # Set the stop event
                    current_training_thread.join() # Wait for the thread to stop, which should happen promptly because of the stop flag
            else:
                self.message_user(request, "No training job is currently running.", level=messages.WARNING)
                

            # Reset job status to 'PENDING' after the job is stopped
            job.status = 'PENDING'
            job.save()  
            clear_event(job_id) # Clear the stop event
            # Depending on the implementation, we may want to delete the output model file here
            
            # Display success message
            self.message_user(request, "Training job stopped successfully.", level=messages.SUCCESS)

        except Exception as e:
            job.status = 'ERROR'
            job.save()
            self.message_user(request, f"An error occurred: {e}", level=messages.ERROR)

        return redirect('/admin/myapp/trainingjob/')  # Redirect back to the change list        
    
    def _train_model_in_background(self, job_id):
        """Function to ensure database integrity when a thread is opened. """
        try:
            with transaction.atomic():  # Ensure database integrity
                #train_ai_model(job_id)
                testTraining(job_id)
        except Exception as e:
            # Log error as status in the database
            job = TrainingJob.objects.get(id=job_id)
            job.status = 'ERROR'
            job.save()

            print(f"Error during training: {e}")
        finally:
            global current_training_thread
            current_training_thread = None
    
    
    def button(self, obj):
        if obj.status == 'PENDING':
            return format_html('<a class="button" href="{}">Start</a>', f'start/{obj.id}')
        elif obj.status == 'IN_PROGRESS':
            return format_html('<a class="button" href="{}">Stop</a>', f'stop/{obj.id}')
        elif obj.status == 'COMPLETED':
            return format_html('<a class="button" href="{}" disabled>Completed</a>', f'')
        else:
            return format_html('<a class="button" href="{}" disabled>ERROR</a>', f'')
    

    button.allow_tags = True

    list_display = ('id', 'dataset', 'status', 'started_at', 'completed_at', 'button')

def get_detector(model_path):
    # Check if the model exists
    if not os.path.exists(model_path):
        raise FileNotFoundError("The hand_landmarker Model not found")

    # Setup the HandLandmarker model configuration
    base_options = mp.tasks.BaseOptions(model_asset_path=model_path)
    options = mp.tasks.vision.HandLandmarkerOptions(base_options=base_options, num_hands=2)
    return mp.tasks.vision.HandLandmarker.create_from_options(options)

def get_landmarks(video_path, detector, show_landmarks=False):
    cap = cv.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError("The video file not found")
    result = []
    num_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        detection_result = detector.detect(mp_image)
        hand_landmarks = detection_result.hand_landmarks
        if hand_landmarks:
            result.append([[[landmark.x, landmark.y, landmark.z] for landmark in hand] for hand in hand_landmarks])
        if show_landmarks:
            if hand_landmarks:
                for hand_landmark in hand_landmarks:
                    normal_list = landmark_pb2.NormalizedLandmarkList()
                    normal_list.landmark.extend([
                        landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmark
                    ])
                    mp.solutions.drawing_utils.draw_landmarks(frame, normal_list, mp.solutions.hands.HAND_CONNECTIONS)
                cv.imshow('Hand Landmarks', frame)
            if cv.waitKey(50) & 0xFF == ord('q'):
                break
    cap.release()
    return result, num_frames


def get_data(words, path, detector_path):
    detector = ld.get_detector(detector_path)

    X = []
    y = []

    num_videos = 0
    highest_frame = 0

    bad_videos = 0

    for word in tqdm(words):
        word_path = os.path.join(path, word)
        
        video_files = [f for f in os.listdir(word_path) if f.endswith('.mp4')]
        
        for video_file in tqdm(video_files, desc=word):
            video_path = os.path.join(word_path, video_file)
            
            try:
                video_X = []
                landmarks, current_frames = ld.get_landmarks(video_path, detector)
                
                if len(landmarks) == 0:
                    bad_videos+=1
                    continue
                
                if current_frames > highest_frame:
                    highest_frame = current_frames
                
                for frame in range(len(landmarks)):
                    features = np.array(landmarks[frame]).flatten()
                    video_X.append(features)
                
                X.append(video_X)
                y.append(words.index(word))
                num_videos += 1

            except Exception as e:
                print(f"Error processing video {video_file}: {e}")
                continue 

    return X, y, num_videos, highest_frame, bad_videos

def padX(X, num_videos, highest_frame, num_features):
    padded_X = np.zeros((num_videos, highest_frame, num_features))
    mask = np.ones((num_videos, highest_frame, num_features)) 
    for i in range(num_videos):
        video = X[i]
        for j in range(len(video)):
            frame = video[j]
            if len(frame) < num_features:
                padded_X[i, j, :] = np.pad(frame, (0, num_features - len(frame)), 'constant')
                mask[i, j, len(frame):] = 0
            else:
                padded_X[i, j, :] = frame
        if len(video) < highest_frame:
            mask[i, len(video):, :] = 0

    return padded_X, mask

def mainPipeline():

    words = ['deaf', 'eat', 'fish', 'friend', 'like', 'milk', 'nice', 'no', 'orange', 'teacher', 'want', 'what', 'where', 'yes']
    select_words = ['no', 'eat', 'teacher', 'want', 'fish']
    path = '../preprocessing/dataset/'
    num_features = 126
    model_name = 'draft_model'
    fps = 20

    X, y, num_videos, highest_frame, bad_videos = get_data(select_words, path, '../models/hand_landmarker.task')

    print('Number of videos:', num_videos)
    print('Highest frame:', highest_frame)
    print('Videos with no landmarkers detected: ', bad_videos)

    ########################################################

    padded_X, mask = padX(X, num_videos, highest_frame, num_features)
    print(padded_X.shape)

    ########################################################
    model = keras.Sequential()

    model.add(keras.Input(shape=(highest_frame, num_features)))
    model.add(layers.Masking(mask_value=0.0))
    model.add(layers.LSTM(64))
    model.add(layers.Dense(32, activation='relu'))
    model.add(layers.Dropout(0.5))
    model.add(layers.Dense(len(select_words), activation='sigmoid'))


    model.summary()

    ########################################################

    X_train, X_temp, y_train, y_temp = train_test_split(padded_X, y, test_size=0.3, random_state=42) 
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42) 


    X_train = np.array(X_train)
    X_val = np.array(X_val)
    X_test = np.array(X_test)
    y_train = np.array(y_train)
    y_val = np.array(y_val)
    y_test = np.array(y_test)

    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    model.fit(X_train, y_train, epochs=10, validation_data=(X_val, y_val))

    model.save(f'../models/{model_name}.keras')

    with open(f"../models/{model_name}.env", "w") as file:
        file.write(f"MAX_FRAMES={highest_frame}\n")
        file.write(f"NUM_FEATURES={num_features}\n")
        #file.write(f"WORDS={",".join(select_words)} \n")
        file.write(f"FPS={fps}\n")

    ########################################################

    results = model.evaluate(X_test, y_test)

    print('Test loss:', results)

    ########################################################

    i = random.randint(0,X_test.shape[0]-1)


    X_prediction = X_test[i,:,:]
    y_prediction = select_words[y_test[i]]

    print(model.predict(np.array([X_prediction])))
    print("should be", y_prediction)
    print("predicted", select_words[np.argmax(model.predict(np.array([X_prediction])))])
@admin.register(TrainedModel)
class TrainedModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'uploaded_at')
    readonly_fields = ('uploaded_at',)

