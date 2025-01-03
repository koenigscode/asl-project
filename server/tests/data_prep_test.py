"""
File: data_prep_test.py
Description: Unit tests for the data_prep.py file.

Contributors:
Adam Faundez Laurokari

Created: 2025-01-02
Last Modified: 2025-01-02

Project: A Sign From Above
URL: https://git.chalmers.se/courses/dit826/2024/group4

License: MIT License (see LICENSE file for details)
"""

import unittest
import numpy as np
import sys
sys.path.insert(1, 'model_training/')
import data_prep as prep

# Test cases for data_prep.py
class TestDataPrep(unittest.TestCase):
    # Test if the function read_files returns the correct output (not None)
    def test_get_data(self):
        words = ['no', 'teacher']
        path = 'tests/test_dataset/'
        detector_path = './models/hand_landmarker.task'
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
        path = './invalid/videopath/'
        detector_path = './models/hand_landmarker.task'
        with self.assertRaises(FileNotFoundError):
            prep.get_data(words, path, detector_path)
    
    # Test if the function read_files raises an exception when using invalid words
    def test_get_data_invalid_words(self):
        words = ['invalid', 'words']
        path = 'tests/test_dataset/'
        detector_path = './models/hand_landmarker.task'
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

    # Test if get_word_accuracy returns the correct output with no data
    def test_get_word_accuracy_no_data(self):
        accuracy = prep.get_word_accuracy(["no"], None, np.array([]), np.array([]))
        self.assertEqual(accuracy, {"no": [0,0]})

    # Test if get_word_accuracy returns an exception when the model is None
    def test_get_word_accuracy_no_model(self):
        with self.assertRaises(AttributeError):
            prep.get_word_accuracy(["no"], None, np.array([[[1]]]), np.array([0]))