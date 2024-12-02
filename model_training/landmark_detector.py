# Credits for template:
# https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/python#video


import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2
import os
import cv2 as cv

def get_detector():
    
    # Check if the model exists
    model_path = os.path.abspath('./models/hand_landmarker.task')
    if not os.path.exists(model_path):
        raise FileNotFoundError("The hand_landmarker Model not found")

    # Setup the HandLandmarker model configuration
    base_options = mp.tasks.BaseOptions(model_asset_path=model_path)
    options = mp.tasks.vision.HandLandmarkerOptions(base_options=base_options, num_hands=2)
    return mp.tasks.vision.HandLandmarker.create_from_options(options)

def get_landmarks(video_path, detector, show_landmarks=False):
    cap = cv.VideoCapture(video_path)
    all_landmarks = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        detection_result = detector.detect(mp_image)
        hand_landmarks = detection_result.hand_landmarks
        all_landmarks.append(hand_landmarks)
        if show_landmarks:
            if hand_landmarks:
                normal_list = landmark_pb2.NormalizedLandmarkList()
                normal_list.landmark.extend([
                landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks[0]
                ])
                mp.solutions.drawing_utils.draw_landmarks(frame, normal_list, mp.solutions.hands.HAND_CONNECTIONS)
                cv.imshow('Hand Landmarks', frame)
            if cv.waitKey(1000) & 0xFF == ord('q'):
                break
    cap.release()
    cv.destroyAllWindows()
    return all_landmarks


if __name__ == '__main__':
    detector = get_detector()
    video_path = 'preprocessing/dataset/train/like/0005.mp4'
    landmarks = get_landmarks(video_path, detector, True)
    print(landmarks)