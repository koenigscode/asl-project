"""
File: models.py
Description: Source code which defines database schema using the ORM system.

Contributors:
Michael Koenig
Sofia Serbina
Parisa Babaei
David Schoen

Created: 2024-11-27
Last Modified: 2025-01-01

Project: A Sign From Above
URL: https://git.chalmers.se/courses/dit826/2024/group4

License: MIT License (see LICENSE file for details)
"""

from django.db import models
from django.core.exceptions import ValidationError
from keras.models import load_model
import logging

logger = logging.getLogger('asl')

# Custom validator to ensure that the uploaded file is a ZIP file
def validate_zip_file(value):
    if not value.name.endswith('.zip'):
        raise ValidationError('Only ZIP files are allowed.')

# Custom validator to ensure that the uploaded file is a Keras model file
def validate_keras_file(value):
    if not value.name.endswith('.keras'):
        raise ValidationError('Only keras files are allowed.')
    
# Dataset model to store the uploaded dataset
class Dataset(models.Model):
    name = models.CharField(max_length=100, unique=True)
    data_file = models.FileField(
        upload_to='datasets/',
        validators=[validate_zip_file],
        help_text=(
            "Upload a ZIP file containing your dataset. "
            "The ZIP file must contain a single root directory, "
            "which includes folders for each word. <br/><br/>"
            "dataset_name.zip/ <br/>"
            "└── dataset_name/ <br/>"
            "....├── apple/ <br/>"
            "....├── hello/ <br/>"
            "....└── love/<br/><br/>"
            "(this may take a moment to validate)"
        )
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    root_directory = models.CharField(max_length=255, editable=False)

    def __str__(self):
        return self.name

# TrainedModel model to store the trained models
class TrainedModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    model_file = models.FileField(upload_to='models/', validators=[validate_keras_file])
    max_frames = models.IntegerField(null=True, blank=True)
    num_features = models.IntegerField(null=True, blank=True)
    accuracy = models.FloatField(null=True, blank=True)
    words = models.TextField(null=True, blank=True, help_text='List of words in the model  (comma separated)')
    fps = models.FloatField(null=True, blank=True)
    word_accuracy = models.JSONField(default=dict, blank=True, help_text='Word accuracy in the model')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False, help_text="Set this model as the one in use")
    model = None

    @classmethod
    def change_model(cls):
        active_model = cls.get_active_model_path()
        cls.model = load_model(active_model)
        print(f"Model '{active_model}' loaded")
        return cls.model

    @classmethod
    def get_active_model_path(cls):
        active_model = cls.objects.filter(is_active=True).first()
        if not active_model:
            logger.error("No active model found")
        return active_model.model_file.path

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # disable other models
        if self.is_active:
            TrainedModel.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)
        self.change_model()

# TrainingJob model to store the training jobs
class TrainingJob(models.Model):
    name = models.CharField(max_length=100, unique=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    base_model = models.ForeignKey(TrainedModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='training_jobs')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='PENDING', editable=False)
    output_model = models.OneToOneField(TrainedModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='output_from_job',editable=False)
    # TODO: Ensure that a trainingJob can't be deleted if it is 'IN_PROGRESS'

    def __str__(self):
        return f"Job {self.id} - {self.status}"
