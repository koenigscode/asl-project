import landmark_detector as ld
import os
import numpy as np
from tqdm.notebook import tqdm

# Function that processes videos and extracts landmarks using the landmark detector
def get_data(words, path, detector_path):
    detector = ld.get_detector(detector_path)

    X = []
    y = []

    num_videos = 0
    highest_frame = 0

    bad_videos = 0
    print("data prep")

    # Loop through each word using tqdm to show progress bar
    for word in tqdm(words):
        print(word)
        word_path = os.path.join(path, word)
        
        video_files = [f for f in os.listdir(word_path) if f.endswith('.mp4')]
        
        for video_file in tqdm(video_files, desc=word):
            video_path = os.path.join(word_path, video_file)
            
            try:
                video_X = []
                # Use the landmark detector function to get the landmarks and current frames
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


# Function that pads the data to the highest frame and feature length
def padX(X, num_videos, highest_frame, num_features):
    padded_X = np.zeros((num_videos, highest_frame, num_features))
    mask = np.ones((num_videos, highest_frame, num_features)) 

    for i in range(num_videos):
        video = X[i]
        for j in range(len(video)):
            frame = video[j]
            if len(frame) < num_features:
                # Pad the frame with zeros if it is less than the number of features
                padded_X[i, j, :] = np.pad(frame, (0, num_features - len(frame)), 'constant')
                mask[i, j, len(frame):] = 0
            else:
                padded_X[i, j, :] = frame
        if len(video) < highest_frame:
            mask[i, len(video):, :] = 0
    return padded_X, mask


# Function that gets the word accuracy of the model on the test set
def get_word_accuracy(select_words, model, X_test, y_test):
    dic = {}
    for word in select_words:
        dic[word] = [0,0]

    for i in range(X_test.shape[0]):
        X_prediction = X_test[i,:,:]
        y_prediction = select_words[y_test[i]]

        # Get the prediction of the model and get the word with the highest probability
        prediction = select_words[np.argmax(model.predict(np.array([X_prediction]), verbose=0))]
        if y_prediction == prediction:
            dic[y_prediction][0] += 1
        dic[y_prediction][1] += 1

    return dic