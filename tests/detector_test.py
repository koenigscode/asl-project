import unittest
import os
import model_training.landmark_detector as ld

class TestLandmarkDetector(unittest.TestCase):
    def test_get_detector(self):
        model_path = os.path.abspath('./models/hand_landmarker.task')
        detector = ld.get_detector(model_path)
        self.assertIsNotNone(detector)
    
    def test_get_detector_bad_modelpath(self):
        model_path = os.path.abspath('./models/non-existent.task')
        with self.assertRaises(FileNotFoundError):
            ld.get_detector(model_path)
    
    def test_get_landmarks(self):
        model_path = os.path.abspath('./models/hand_landmarker.task')
        detector = ld.get_detector(model_path)
        video_path = 'preprocessing/dataset/test/teacher/0004.mp4'
        landmarks, frames = ld.get_landmarks(video_path, detector)
        self.assertIsNotNone(landmarks)
        self.assertIsNotNone(frames)

    def test_get_landmarks_bad_videopath(self):
        model_path = os.path.abspath('./models/hand_landmarker.task')
        detector = ld.get_detector(model_path)
        video_path = 'preprocessing/dataset/test/teacher/0000.mp4'
        with self.assertRaises(FileNotFoundError):
            ld.get_landmarks(video_path, detector)


if __name__ == '__main__':
    unittest.main()