# Credits for template:
# https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/python#video


import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2
import os
import cv2 as cv

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


if __name__ == '__main__':
    model_path = os.path.abspath('./models/hand_landmarker.task')
    detector = get_detector(model_path)
    video_path = 'preprocessing/dataset/train/eat/0001.mp4'
    landmarks, frames = get_landmarks(video_path, detector)
    print(landmarks)
    print(frames)