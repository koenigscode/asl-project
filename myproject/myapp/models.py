from django.db import models
from django.core.exceptions import ValidationError
import os

# Create your models here.
def validate_zip_file(value):
    if not value.name.endswith('.zip'):
        raise ValidationError('Only ZIP files are allowed.')

def validate_pth_file(value):
    if not value.name.endswith('.pth'):
        raise ValidationError('Only pth files are allowed.')
    
class Dataset(models.Model):
    name = models.CharField(max_length=100, unique=True)
    data_file = models.FileField(upload_to='datasets/', validators=[validate_zip_file])
    uploaded_at = models.DateTimeField(auto_now_add=True)
    root_directory = models.CharField(max_length=255, editable=False)

    def __str__(self):
        return self.name

class TrainedModel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    model_file = models.FileField(upload_to='trained_models/', validators=[validate_pth_file])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class TrainingJob(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    base_model = models.ForeignKey(TrainedModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='training_jobs')
    hyperparameters = models.JSONField()
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50)
    output_model = models.OneToOneField(TrainedModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='output_from_job')

    def __str__(self):
        return f"Job {self.id} - {self.status}"
    
class TrainingMetrics(models.Model):
    job = models.ForeignKey(TrainingJob, on_delete=models.CASCADE, related_name='metrics')
    epoch = models.IntegerField()
    loss = models.FloatField()
    accuracy = models.FloatField()

    def __str__(self):
        return f"Job {self.job.id} - Epoch {self.epoch}"