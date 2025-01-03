"""
File: retrain_test.py
Description: Unit tests for the retrain.py file.

Contributors:
Adam Faundez Laurokari

Created: 2025-01-02
Last Modified: 2025-01-02

Project: A Sign From Above
URL: https://git.chalmers.se/courses/dit826/2024/group4

License: MIT License (see LICENSE file for details)
"""

from unittest import TestCase
from app.retrain import retrain
from app.models import TrainingJob, TrainedModel, Dataset
import os

class RetrainTest(TestCase):
    def test_retrain(self):

        # Create a dataset
        dataset = Dataset()
        dataset.name = 'test_dataset'
        dataset.data_file = 'test_dataset.zip'
        dataset.root_directory = './tests/test_dataset'
        dataset.save()

        # Get base model
        base_model = TrainedModel.objects.get(name='draft_model')

        if not os.path.exists('./tests/test_dataset'):
            os.makedirs('./tests/test_dataset')
        for word in base_model.words.split(','):
            if not os.path.exists(f'./tests/test_dataset/{word}'):
                os.makedirs(f'./tests/test_dataset/{word}')

        # Create a job
        job = TrainingJob()
        job.name = 'test_model'
        job.dataset_id = dataset.id
        job.base_model_id = base_model.id
        job.save()

        job_id = job.id

        # Call the function
        trained_model = retrain(job_id)

        # Check the result
        self.assertIsNotNone(trained_model)
        self.assertEqual(trained_model.name, 'test_model')
        self.assertEqual(trained_model.words, base_model.words)

        # Clean up
        dataset.delete()
        job.delete()
        trained_model.delete()
        os.remove("models/test_model.keras")
        os.remove("models/test_model.env")
        