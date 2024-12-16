from app.landmark_detector import get_detector, get_landmarks
import os
import random
import numpy as np
import keras
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from keras import layers
from app.models import TrainingJob, Dataset, TrainedModel, models
from app.shared_state import get_event

def get_data(words, path, detector_path):
    detector = get_detector(detector_path)

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
                landmarks, current_frames = get_landmarks(video_path, detector)
                
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


def mainPipeline(job_id):

    #here we will use the "job" variable to get the neccisary data from the db
    #job = TrainingJob.objects.get(id=job_id)
    #dataset = ForeignKey
    #base_model
    #hyperparameters

    words = ['deaf', 'eat', 'fish', 'friend', 'like', 'milk', 'nice', 'no', 'orange', 'teacher', 'want', 'what', 'where', 'yes']
    select_words = ['no', 'eat', 'teacher', 'want', 'fish']
    path = './preprocessing/dataset/test'
    num_features = 126
    model_name = 'draft_model'
    fps = 20

    X, y, num_videos, highest_frame, bad_videos = get_data(select_words, path, './models/hand_landmarker.task')

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

    model.save(f'./models/{model_name}.keras')

    with open(f"./models/{model_name}.env", "w") as file:
        file.write(f"MAX_FRAMES={highest_frame}\n")
        file.write(f"NUM_FEATURES={num_features}\n")
        file.write(f"WORDS={','.join(select_words)}\n")
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

if __name__ == "__main__":
    #mainPipeline()
    print("pass")
    pass