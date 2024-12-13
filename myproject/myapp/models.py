from django.db import models
from django.core.exceptions import ValidationError
import os

# Create your models here.
def validate_zip_file(value):
    if not value.name.endswith('.zip'):
        raise ValidationError('Only ZIP files are allowed.')

def validate_keras_file(value):
    if not value.name.endswith('.keras'):
        raise ValidationError('Only keras files are allowed.')
    
class Dataset(models.Model):
    name = models.CharField(max_length=100, unique=True)
    data_file = models.FileField(
        upload_to='datasets/',
        validators=[validate_zip_file],
        help_text=(
            "Upload a ZIP file containing your dataset. "
            "The ZIP file must contain a single root directory, "
            "which includes 'train', 'test', and 'val' folders. <br/><br/>"
            "dataset_name.zip/ <br/>"
            "└── dataset_name/ <br/>"
            "....├── train/ <br/>"
            "....├── test/ <br/>"
            "....└── val/"
        )
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    root_directory = models.CharField(max_length=255, editable=False)

    def __str__(self):
        return self.name

class TrainedModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    model_file = models.FileField(upload_to='trained_models/', validators=[validate_keras_file])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class TrainingJob(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    base_model = models.ForeignKey(TrainedModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='training_jobs')
    hyperparameters = models.JSONField(default=dict, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='PENDING', editable=False)
    output_model = models.OneToOneField(TrainedModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='output_from_job')
    # TODO: Add a field to store the training metrics, which will be a JSON object, and will be added after we implement the training process


    def __str__(self):
        return f"Job {self.id} - {self.status}"
    
class TrainingMetrics(models.Model):
    job = models.ForeignKey(TrainingJob, on_delete=models.CASCADE, related_name='metrics')
    epoch = models.IntegerField()
    loss = models.FloatField()
    accuracy = models.FloatField()

    def __str__(self):
        return f"Job {self.job.id} - Epoch {self.epoch}"