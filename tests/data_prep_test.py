import unittest
import numpy as np
import sys
sys.path.insert(1, '../server/model_training')
import data_prep as prep

# Test cases for data_prep.py
class TestDataPrep(unittest.TestCase):
    # Test if the function read_files returns the correct output (not None)
    def test_get_data(self):
        words = ['no', 'teacher']
        path = '../preprocessing/dataset/'
        detector_path = '../models/hand_landmarker.task'
        X, y, num_videos, highest_frame, bad_videos = prep.get_data(words, path, detector_path)

        self.assertIsNotNone(X)
        self.assertIsNotNone(y)
        self.assertIsNotNone(num_videos)
        self.assertIsNotNone(bad_videos)
        self.assertIsNotNone(highest_frame)
        self.assertGreater(num_videos, 0)
        self.assertGreater(highest_frame, 0)
    
    # Test if the function read_files raises an exception when the path is invalid
    def test_get_data_invalid_videopath(self):
        words = ['no', 'teacher']
        path = '../invalid/videopath/'
        detector_path = '../models/hand_landmarker.task'
        with self.assertRaises(FileNotFoundError):
            prep.get_data(words, path, detector_path)
    
    # Test if the function read_files raises an exception when using invalid words
    def test_get_data_invalid_words(self):
        words = ['invalid', 'words']
        path = '../preprocessing/dataset/'
        detector_path = '../models/hand_landmarker.task'
        with self.assertRaises(FileNotFoundError):
            prep.get_data(words, path, detector_path)

    # Test if the function padX returns the correct output (not None)
    def test_padX(self):
        X = [[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10], [13, 14, 15]]]
        expected_padded_X = [[[1, 2, 3], [4, 5, 6], [0, 0, 0]], [[7, 8, 9], [10, 0, 0], [13, 14, 15]]]
        num_videos = 2
        highest_frame = 3
        num_features = 3
        padded_X, mask = prep.padX(X, num_videos, highest_frame, num_features)
        self.assertIsNotNone(padded_X)
        self.assertIsNotNone(mask)
        self.assertEqual(padded_X.shape, (2, 3, 3))
        self.assertEqual(mask.shape, (2, 3, 3))
        self.assertTrue(np.array_equal(padded_X, expected_padded_X))

if __name__ == '__main__':
    unittest.main()