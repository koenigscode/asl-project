from unittest import TestCase
from app import prediction
import time
import os

class PredictionTest(TestCase):

    def test_generate_random_hash(self):
        hash = prediction.generate_random_hash()
        self.assertIsNotNone(hash)

    def test_save_recording(self):
        relative_path = './tests/test_dataset/teacher/3e10848fd5.mp4'
        full_path = os.path.abspath(relative_path)
        output = prediction.save_recording(full_path, 'teacher')
        self.assertIsNotNone(output)

    def test_predict(self):
        relative_path = './tests/test_dataset/teacher/3e10848fd5.mp4'
        full_path = os.path.abspath(relative_path)
        output = prediction.predict(full_path, 'teacher', False)
        self.assertIsNotNone(output)

    def test_predict_latency(self):
        latencies =  []
        paths = ['./tests/test_dataset/no/0c85845c97.mp4', './tests/test_dataset/teacher/3e10848fd5.mp4']

        for path in paths:
            full_path = os.path.abspath(path)
            start_time = time.time()
            prediction.predict(full_path, 'teacher', False)
            end_time = time.time()
            latencies.append(end_time - start_time)
        
        print("Average latency: ", sum(latencies)/len(latencies))
        self.assertLessEqual(sum(latencies)/len(latencies), 5)


