import model_training.landmark_detector as ld
import os
import numpy as np

def get_data(mode, words, path, detector_path):
    detector = ld.get_detector(detector_path)

    training_X = []
    training_y = []

    num_videos = 0
    highest_frame = 0

    for word in words:
        i = 1
        video_path = path + mode + '/' + word + '/0001.mp4'
        while os.path.exists(video_path):
            try:
                video_X = []
                landmarks, current_frames = ld.get_landmarks(video_path, detector)
                if len(landmarks) == 0:
                    i += 1
                    video_path = path + mode + '/' + word + '/' + str(i).zfill(4) + '.mp4'
                    continue
                if current_frames > highest_frame:
                    highest_frame = current_frames
                for frame in range(len(landmarks)):
                    features = np.array(landmarks[frame]).flatten()
                    video_X.append(features)
                training_X.append(video_X)
                training_y.append(words.index(word))
                i += 1
                num_videos += 1
                video_path = path + mode + '/' + word + '/' + str(i).zfill(4) + '.mp4'
            except Exception as e:
                print(e)
                break
    return training_X, training_y, num_videos, highest_frame

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