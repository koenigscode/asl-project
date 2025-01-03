"""
File: admin.py
Description: Source code for functionalities found on the admin UI, ( /admin ). Largely, training models.

Contributors:
Sofia Serbina
Parisa Babaei
David Schoen

Created: 2024-11-27
Last Modified: 2024-12-30

Project: A Sign From Above
URL: https://git.chalmers.se/courses/dit826/2024/group4

License: MIT License (see LICENSE file for details)
"""

import shutil
from django.contrib import admin
from .models import Dataset, TrainingJob, TrainedModel
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
import zipfile
import os
import matplotlib.pyplot as plt
import tempfile
from threading import Thread
from django.db import transaction
from django.conf import settings
from django.http import HttpResponse
from app.shared_state import get_event, clear_event
from .retrain import retrain
import time

#Global variables
MAX_EXTRACT_SIZE = 10000000000
current_training_thread = None


# Admin panel for the Dataset model
@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('name', 'uploaded_at')

    # Customize the form for adding/editing Dataset to include the data_file field
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
        extracted_items = os.listdir(extract_to)
    
        # Filter directories
        extracted_dirs = [item for item in extracted_items if os.path.isdir(os.path.join(extract_to, item))]

        if len(extracted_dirs) != 1:
            # Delete the uploaded ZIP file
            obj.data_file.delete(save=False)
            # Delete the Dataset object from the database
            obj.delete()
            # Remove the extracted files
            shutil.rmtree(extract_to, ignore_errors=True)
            # Display error message
            messages.set_level(request, messages.ERROR)
            self.message_user(request, "The ZIP file must contain a single root directory containing the dataset.", level=messages.ERROR)
            return
        
        obj.root_directory = os.path.join(extract_to, extracted_dirs[0])
        obj.save()

        # If validation passes
        messages.set_level(request, messages.SUCCESS)
        self.message_user(request, 'Dataset uploaded and extracted successfully.', level=messages.SUCCESS)


# Admin panel for the TrainingJob model
@admin.register(TrainingJob)
class TrainingJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'dataset', 'status', 'started_at', 'completed_at', 'button')
    list_filter = ('status',)
    search_fields = ('id', 'dataset__name')
    readonly_fields = ('started_at', 'completed_at')

    # Customize the form for adding/editing TrainingJob
    def get_readonly_fields(self, request, obj=None):
        # editing an existing object
        if obj:
            if obj.status != 'PENDING':
                return  ('dataset', 'base_model',  'status', 'output_model' ) + self.readonly_fields
        return self.readonly_fields

    # Add custom start and stop buttons to the admin panel
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('start/<int:job_id>/', self.admin_site.admin_view(self.start_job), name='trainingjob-start'),
            path('stop/<int:job_id>/', self.admin_site.admin_view(self.stop_job), name='trainingjob-stop')
        ]
        return custom_urls + urls

    # Start the training job
    def start_job(self, request, job_id):
        try:
            # Global variable to check if another training job is already running
            global current_training_thread

            # Here we get the TrainingJob object as a variable and change its status to 'IN_PROGRESS'
            job = TrainingJob.objects.get(id=job_id)
            job.status = 'IN_PROGRESS'
            job.save()

            if current_training_thread is None:
                # Start the training job in a separate thread
                get_event(job_id)
                current_training_thread = Thread(target=self._train_model_in_background, args=(request, job_id,))
                current_training_thread.start()
                self.message_user(request, "Training job started in background.", level=messages.SUCCESS)
            else:
                self.message_user(request, "Another training job is currently running. Cannot start another.", level=messages.WARNING)
                return redirect('/admin/app/trainingjob/')

        except Exception as e:
            job.status = 'ERROR'
            job.save()
            self.message_user(request, str("An error occured, error message: " + e), level=messages.ERROR)

        # Redirect back to the change list
        return redirect('/admin/app/trainingjob/')
    
    # Stop the training job
    def stop_job(self, request, job_id):
        """Stop the job by setting the stop flag and returning to PENDING."""
        try:
            # Global variable to check if another training job is already running
            global current_training_thread

            job = TrainingJob.objects.get(id=job_id)

            # Check if the job is currently running
            if job.status != 'IN_PROGRESS':
                self.message_user(request, "The job is not currently running.", level=messages.WARNING)
                return redirect('/admin/app/trainingjob/')

            # Wait for the training thread to stop
            if current_training_thread is not None and current_training_thread.is_alive():
                    # Set the stop event
                    get_event(job_id).set()
                    # Wait for the thread to stop, which should happen promptly because of the stop flag
                    current_training_thread.join()
            else:
                self.message_user(request, "No training job is currently running.", level=messages.WARNING)
                

            # Reset job status to 'PENDING' after the job is stopped
            job.status = 'PENDING'
            job.save()  
            # Clear the stop event
            clear_event(job_id)
            # Depending on the implementation, we may want to delete the output model file here
            
            # Display success message
            self.message_user(request, "Training job stopped successfully.", level=messages.SUCCESS)

        except Exception as e:
            job.status = 'ERROR'
            job.save()
            self.message_user(request, f"An error occurred: {e}", level=messages.ERROR)

        # Redirect back to the change list 
        return redirect('/admin/app/trainingjob/')       
    
    # Function to train the model in the background
    def _train_model_in_background(self, request, job_id):
        """Function to ensure database integrity when a thread is opened. """
        try:
            # Ensure database integrity
            with transaction.atomic():
                retrain(job_id)
                i = 0
                while (i > 10):
                    print(i)
                    time.sleep(1) #this doesn't really work it seems, likely because _train_model_in_background is being executed by non-main thread
                    i += 1
                job = TrainingJob.objects.get(id=job_id)
                job.status = 'COMPLETED'
                job.save()
                self.message_user(request, "The training has been completed", level=messages.SUCCESS)
    
        except Exception as e:
            # Log error as status in the database
            job = TrainingJob.objects.get(id=job_id)
            job.status = 'ERROR'
            job.save()

            print(f"Error during training: {e}")
        finally:
            global current_training_thread
            current_training_thread = None
    
    
    # Add a custom button to the admin panel to start or stop the training job
    def button(self, obj):
        if obj.status == 'PENDING':
            return format_html('<a class="button" href="{}">Start</a>', f'start/{obj.id}/')
        elif obj.status == 'IN_PROGRESS':
            return format_html('<a class="button" href="{}">Stop</a>', f'stop/{obj.id}/')
        elif obj.status == 'COMPLETED':
            return format_html('<a class="button" href="{}" disabled>Completed</a>', f'')
        else:
            return format_html('<a class="button" href="{}" disabled>ERROR</a>', f'')
    

    button.allow_tags = True


# Admin panel for the TrainedModel model
@admin.register(TrainedModel)
class TrainedModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'accuracy_percentage', 'uploaded_at')
    readonly_fields = ('uploaded_at',)
    search_fields = ('name',)
    actions = ['create_accuracy_graph']

    # Display accuracy as a percentage
    def accuracy_percentage(self, obj):
        return f"{obj.accuracy * 100:.2f}%"
    accuracy_percentage.short_description = 'Accuracy'

    # Customize the form for adding/editing TrainedModel to include the model_file field
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Save model info as dotenv file
        with open(os.path.join(settings.MEDIA_ROOT, 'models', obj.name + '.env'), 'w') as file:
            file.write(f"MAX_FRAMES={obj.max_frames}\n")
            file.write(f"NUM_FEATURES={obj.num_features}\n")
            file.write(f"WORDS={obj.words}\n")
            file.write(f"FPS={obj.fps}\n")
            file.write(f"TEST_ACC={obj.accuracy}\n")
            file.write(f'WORD_ACC="{obj.word_accuracy}"\n')

    # Create a graph of the accuracy by word for the selected models
    def create_accuracy_graph(self, request, queryset):
        words = set()
        model_accuracies = {}

        # Collect all words and their accuracies
        for model in queryset:
            model_accuracies[model.name] = {}
            for word, count in model.word_accuracy.items():
                if word not in model_accuracies[model.name]:
                    model_accuracies[model.name][word] = []
                if count[1] != 0:
                    model_accuracies[model.name][word].append(count[0]/count[1])
                else:
                    model_accuracies[model.name][word].append(0)
                words.add(word)

        words = sorted(words)

        # Create the graph
        plt.figure(figsize=(10, 5))
        for model_name, accuracies in model_accuracies.items():
            model_word_accuracies = [accuracies.get(word, 0) for word in words]
            plt.plot(words, model_word_accuracies, label=model_name)

        plt.xlabel('Words')
        plt.ylabel('Accuracy')
        plt.title('Accuracy by Word for Selected Models')
        plt.xticks(rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()

        # Save the graph to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            plt.savefig(tmpfile.name)
            plt.close()
            tmpfile.seek(0)
            response = HttpResponse(tmpfile.read(), content_type="image/png")
            response['Content-Disposition'] = 'inline; filename="accuracy_by_word.png"'
            return response

    create_accuracy_graph.short_description = 'Create accuracy graph for selected models'
