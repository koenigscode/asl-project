from django.db import models
from django.core.exceptions import ValidationError


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

    def __str__(self):
        return self.name

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
