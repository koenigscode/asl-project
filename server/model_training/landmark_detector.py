"""
File: landmark_detector.py
Description: Source code which uses a detector to find the landmarks in a video.
Returns a video with detected landmarks.

Contributors:
Parisa Babaei
Adam Faundez Laurokari

Created: 2024-12-16
Last Modified: 2025-01-02

Project: A Sign From Above
URL: https://git.chalmers.se/courses/dit826/2024/group4

License: MIT License (see LICENSE file for details)
"""

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

    # Loop through the video frames
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

        # Detect the hand landmarks
        detection_result = detector.detect(mp_image)
        hand_landmarks = detection_result.hand_landmarks

        # Append the landmarks to the result list
        if hand_landmarks:
            result.append([[[landmark.x, landmark.y, landmark.z] for landmark in hand] for hand in hand_landmarks])
        
        # Show the landmarks if needed
        if show_landmarks:
            if hand_landmarks:
                for hand_landmark in hand_landmarks:
                    # Use the mediapipe drawing utilities to draw the landmarks
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
