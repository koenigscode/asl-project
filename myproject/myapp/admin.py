import shutil
from django.contrib import admin
from .models import Dataset, TrainingJob, TrainedModel
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
import zipfile
import os
from django.conf import settings
from django.core.exceptions import ValidationError

#global variables
MAX_EXTRACT_SIZE = 10000000000

# Register your models here.
def validate_dataset_structure(extract_to):
    # List items in the extracted directory
    extracted_items = os.listdir(extract_to)
    
    # Filter directories
    extracted_dirs = [item for item in extracted_items if os.path.isdir(os.path.join(extract_to, item))]
    
    # Ensure there is exactly one root directory
    if len(extracted_dirs) != 1:
        return False, "The ZIP file must contain a single root directory containing the dataset."
    
    dataset_root = extracted_dirs[0]
    dataset_root_path = os.path.join(extract_to, dataset_root)
    
    # Now check for 'train', 'test', 'val' under the dataset root directory
    required_dirs = {'train', 'test', 'val'}
    extracted_subdirs = set(os.listdir(dataset_root_path))
    
    missing_dirs = required_dirs - extracted_subdirs
    if missing_dirs:
        return False, f"Missing required folders under '{dataset_root}': {', '.join(missing_dirs)}"
    
    return True, "Dataset structure is valid."

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('name', 'uploaded_at')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        zip_path = obj.data_file.path
        extract_to = os.path.join(settings.MEDIA_ROOT, 'datasets', obj.name)

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Security: Check for path traversal
                for member in zip_ref.namelist():
                    member_path = os.path.join(extract_to, member)
                    abs_member_path = os.path.abspath(member_path)
                    if not abs_member_path.startswith(os.path.abspath(extract_to)):
                        raise Exception("Attempted Path Traversal in ZIP File")

                # Security: Check for ZIP bombs
                total_size = sum([zinfo.file_size for zinfo in zip_ref.infolist()])
                if total_size > MAX_EXTRACT_SIZE:
                    raise Exception("Extracted content exceeds the maximum allowed size. size:" + str(total_size))

                zip_ref.extractall(extract_to)
        except Exception as e:
            messages.set_level(request, messages.ERROR)
            self.message_user(request, str(e), level=messages.ERROR)
            obj.delete()
            shutil.rmtree(extract_to, ignore_errors=True)
            return

        # Validate the dataset structure
        is_valid, message = validate_dataset_structure(extract_to)
        if not is_valid:
            # **Delete the uploaded ZIP file**
            obj.data_file.delete(save=False)
            # Delete the Dataset object from the database
            obj.delete()
            # Remove the extracted files
            shutil.rmtree(extract_to, ignore_errors=True)
            # Display error message
            messages.set_level(request, messages.ERROR)
            self.message_user(request, message, level=messages.ERROR)
            return

        # If validation passes
        messages.set_level(request, messages.SUCCESS)
        self.message_user(request, 'Dataset uploaded and extracted successfully.', level=messages.SUCCESS)


@admin.register(TrainingJob)
class TrainingJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'dataset', 'status', 'started_at', 'completed_at')
    list_filter = ('status',)
    search_fields = ('id', 'dataset__name')
    readonly_fields = ('started_at', 'completed_at')

    # Customize the form for adding/editing TrainingJob
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('dataset', 'hyperparameters')
        return self.readonly_fields

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('start/<int:job_id>/', self.admin_site.admin_view(self.start_job), name='trainingjob-start'),
            # Add more paths for pause, resume, stop
        ]
        return custom_urls + urls

    def start_job(self, request, job_id):
        # Logic to start the job using PyTorch
        # For example, enqueue the job in a task queue
        self.message_user(request, "Training job started successfully.", level=messages.SUCCESS)
        return redirect('..')  # Redirect back to the change list

    def start_training(self, obj):
        return format_html('<a class="button" href="{}">Start</a>', f'start/{obj.id}')
    start_training.short_description = 'Start Training'
    start_training.allow_tags = True

    list_display = ('id', 'dataset', 'status', 'started_at', 'completed_at', 'start_training')

@admin.register(TrainedModel)
class TrainedModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'uploaded_at')
    readonly_fields = ('uploaded_at',)