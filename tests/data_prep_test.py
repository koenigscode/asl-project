import unittest
import model_training.data_prep as prep

class TestDataPrep(unittest.TestCase):
    def test_get_data(self):
        words = ['no', 'teacher']
        path = './preprocessing/dataset/'
        detector_path = './models/hand_landmarker.task'
        training_X, training_y, num_videos, highest_frame = prep.get_data('train', words, path, detector_path)

        self.assertIsNotNone(training_X)
        self.assertIsNotNone(training_y)
        self.assertIsNotNone(num_videos)
        self.assertIsNotNone(highest_frame)
        
        self.assertGreater(num_videos, 0)
        self.assertGreater(highest_frame, 0)
    
    def test_get_data_invalid_videopath(self):
        words = ['no', 'teacher']
        path = './invalid/videopath/'
        detector_path = './models/hand_landmarker.task'
        training_X, training_y, num_videos, highest_frame = prep.get_data('train', words, path, detector_path)

        self.assertIsNotNone(training_X)
        self.assertIsNotNone(training_y)
        self.assertEqual(num_videos, 0)
        self.assertEqual(highest_frame, 0)
    
    def test_get_data_invalid_words(self):
        words = ['invalid', 'words']
        path = './preprocessing/dataset/'
        detector_path = './models/hand_landmarker.task'
        training_X, training_y, num_videos, highest_frame = prep.get_data('train', words, path, detector_path)

        self.assertIsNotNone(training_X)
        self.assertIsNotNone(training_y)
        self.assertEqual(num_videos, 0)
        self.assertEqual(highest_frame, 0)

    def test_padX(self):
        X = [[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10, 11, 12], [13, 14, 15]]]
        num_videos = 2
        highest_frame = 3
        num_features = 3
        padded_X, mask = prep.padX(X, num_videos, highest_frame, num_features)
        self.assertIsNotNone(padded_X)
        self.assertIsNotNone(mask)

if __name__ == '__main__':
    unittest.main()