import unittest
import os
import sys

sys.path.insert(1, 'model_training/')
import landmark_detector as ld

# Test cases for landmark_detector.py
class TestLandmarkDetector(unittest.TestCase):
    # Test if the function get_detector returns the correct output (not None)
    def test_get_detector(self):
        model_path = os.path.abspath('./models/hand_landmarker.task')
        detector = ld.get_detector(model_path)
        self.assertIsNotNone(detector)
    
    # Test if the function get_detector raises an exception when the model path is invalid
    def test_get_detector_bad_modelpath(self):
        model_path = os.path.abspath('./models/non-existent.task')
        with self.assertRaises(FileNotFoundError):
            ld.get_detector(model_path)
    
    # Test if the function get_landmarks returns the correct output (not None)
    def test_get_landmarks(self):
        model_path = os.path.abspath('./models/hand_landmarker.task')
        detector = ld.get_detector(model_path)
        video_path = 'tests/test_dataset/teacher/3e10848fd5.mp4'
        landmarks, frames = ld.get_landmarks(video_path, detector, True)
        self.assertIsNotNone(landmarks)
        self.assertIsNotNone(frames)

    # Test if the function get_landmarks raises an exception when the video path is invalid
    def test_get_landmarks_bad_videopath(self):
        model_path = os.path.abspath('./models/hand_landmarker.task')
        detector = ld.get_detector(model_path)
        video_path = '../invalid/0000.mp4'
        with self.assertRaises(FileNotFoundError):
            ld.get_landmarks(video_path, detector)