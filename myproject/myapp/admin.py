import shutil
from django.contrib import admin
from .models import Dataset, TrainingJob, TrainedModel
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
import zipfile
import os
from threading import Thread
from django.db import transaction
from django.conf import settings
from django.core.exceptions import ValidationError
from .utils import validate_dataset_structure, train_model
from .testTraining import testTraining
from .shared_state import get_event, clear_event

#Global variables
MAX_EXTRACT_SIZE = 10000000000
current_training_thread = None

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
            path('stop/<int:job_id>/', self.admin_site.admin_view(self.stop_job), name='trainingjob-stop')
        ]
        return custom_urls + urls

    def start_job(self, request, job_id):
        try:
            global current_training_thread

            # Here we get the TrainingJob object as a variable and change its status to 'IN_PROGRESS'
            job = TrainingJob.objects.get(id=job_id)
            job.status = 'IN_PROGRESS'
            job.save()

            if current_training_thread is None:
                # Start the training job in a separate thread
                get_event(job_id) # Create a stop event for the job
                current_training_thread = Thread(target=self._train_model_in_background, args=(job_id,))
                current_training_thread.start()
                self.message_user(request, "Training job started in background.", level=messages.SUCCESS)
            else:
                self.message_user(request, "Another training job is currently running. Cannot start another.", level=messages.WARNING)
                return redirect('/admin/myapp/trainingjob/')

        except Exception as e:
            job.status = 'ERROR'
            job.save()
            self.message_user(request, str("An error occured, error message: " + e), level=messages.ERROR)

        return redirect('/admin/myapp/trainingjob/')  # Redirect back to the change list
    
    def stop_job(self, request, job_id):
        """Stop the job by setting the stop flag and returning to PENDING."""
        try:
            global current_training_thread

            job = TrainingJob.objects.get(id=job_id)

            if job.status != 'IN_PROGRESS':
                self.message_user(request, "The job is not currently running.", level=messages.WARNING)
                return redirect('/admin/myapp/trainingjob/')

            # Wait for the training thread to stop
            if current_training_thread is not None and current_training_thread.is_alive():
                    get_event(job_id).set() # Set the stop event
                    current_training_thread.join() # Wait for the thread to stop, which should happen promptly because of the stop flag
            else:
                self.message_user(request, "No training job is currently running.", level=messages.WARNING)
                

            # Reset job status to 'PENDING' after the job is stopped
            job.status = 'PENDING'
            job.save()  
            clear_event(job_id) # Clear the stop event
            # Depending on the implementation, we may want to delete the output model file here
            
            # Display success message
            self.message_user(request, "Training job stopped successfully.", level=messages.SUCCESS)

        except Exception as e:
            job.status = 'ERROR'
            job.save()
            self.message_user(request, f"An error occurred: {e}", level=messages.ERROR)

        return redirect('/admin/myapp/trainingjob/')  # Redirect back to the change list        
    
    def _train_model_in_background(self, job_id):
        """Function to ensure database integrity when a thread is opened. """
        try:
            with transaction.atomic():  # Ensure database integrity
                #train_ai_model(job_id)
                testTraining(job_id)
        except Exception as e:
            # Log error as status in the database
            job = TrainingJob.objects.get(id=job_id)
            job.status = 'ERROR'
            job.save()

            print(f"Error during training: {e}")
        finally:
            global current_training_thread
            current_training_thread = None
    
    
    def button(self, obj):
        if obj.status == 'PENDING':
            return format_html('<a class="button" href="{}">Start</a>', f'start/{obj.id}')
        elif obj.status == 'IN_PROGRESS':
            return format_html('<a class="button" href="{}">Stop</a>', f'stop/{obj.id}')
        elif obj.status == 'COMPLETED':
            return format_html('<a class="button" href="{}" disabled>Completed</a>', f'')
        else:
            return format_html('<a class="button" href="{}" disabled>ERROR</a>', f'')
    

    button.allow_tags = True

    list_display = ('id', 'dataset', 'status', 'started_at', 'completed_at', 'button')

@admin.register(TrainedModel)
class TrainedModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'uploaded_at')
    readonly_fields = ('uploaded_at',)

