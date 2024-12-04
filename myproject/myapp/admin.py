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
from .utils import validate_dataset_structure, train_model

#Global variables
MAX_EXTRACT_SIZE = 10000000000

#Models

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
            if obj.status != 'PENDING':
                return  ('dataset', 'base_model', 'hyperparameters',  'status', 'output_model' ) + self.readonly_fields
        return self.readonly_fields

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('start/<int:job_id>/', self.admin_site.admin_view(self.start_job), name='trainingjob-start'),
            path('pause/<int:job_id>/', self.admin_site.admin_view(self.pause_job), name='trainingjob-pause'),
            path('resume/<int:job_id>/', self.admin_site.admin_view(self.resume_job), name='trainingjob-resume')
        ]
        return custom_urls + urls

    def start_job(self, request, job_id):
        # Logic to start the job using PyTorch
        try:
            job = TrainingJob.objects.get(id=job_id)
            job.status = 'IN_PROGRESS'
            job.save()

            #TODO: the training is likely to take time, so it should be done in a separate thread so we can continue to use the admin interface
            
            # path_to_model = train_model(job_id)
            #self.message_user(request, "Training job started successfully.", level=messages.SUCCESS)

            self.message_user(request, "training not implemented yet.", level=messages.ERROR)
        except Exception as e:
            job.status = 'ERROR'
            job.save()
            self.message_user(request, str(e), level=messages.ERROR)
        return redirect('/admin/myapp/trainingjob/')  # Redirect back to the change list

    def pause_job(self, request, job_id):
        # Logic to pause the job
        try:
            job = TrainingJob.objects.get(id=job_id)
            job.status = 'PAUSED'
            job.save()
            self.message_user(request, "training not implemented yet.", level=messages.ERROR)
            #self.message_user(request, "Training job paused successfully.", level=messages.SUCCESS)
        except Exception as e:
            job.status = 'ERROR'
            job.save()
            self.message_user(request, str(e), level=messages.ERROR)
        return redirect('/admin/myapp/trainingjob/')  # Redirect back to the change list
    
    def resume_job(self, request, job_id):
        # Logic to resume the job
        try:
            job = TrainingJob.objects.get(id=job_id)
            job.status = 'IN_PROGRESS'
            job.save()
            self.message_user(request, "training not implemented yet.", level=messages.ERROR)
            #self.message_user(request, "Training job resumed successfully.", level=messages.SUCCESS)
        except Exception as e:
            job.status = 'ERROR'
            job.save()
            self.message_user(request, str(e), level=messages.ERROR)
        return redirect('/admin/myapp/trainingjob/')
    
    
    def button(self, obj):
        if obj.status == 'PENDING':
            return format_html('<a class="button" href="{}">Start</a>', f'start/{obj.id}')
        elif obj.status == 'IN_PROGRESS':
            return format_html('<a class="button" href="{}">Pause</a>', f'pause/{obj.id}')
        elif obj.status == 'PAUSED':
            return format_html('<a class="button" href="{}">Resume</a>', f'resume/{obj.id}')
        elif obj.status == 'COMPLETED':
            return format_html('<a class="button" href="{}" disabled>Completed</a>', f'')
        else:
            return format_html('<a class="button" href="{}" disabled>ERROR</a>', f'')
    
    # TODO: make the button changeable depending on the status of the training job

    button.allow_tags = True

    list_display = ('id', 'dataset', 'status', 'started_at', 'completed_at', 'button')

@admin.register(TrainedModel)
class TrainedModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'uploaded_at')
    readonly_fields = ('uploaded_at',)

