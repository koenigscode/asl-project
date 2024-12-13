from django.utils import timezone
from .models import TrainingJob, TrainingMetrics, TrainedModel
from django.conf import settings
import os

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

def train_model(training_job_id):
    # placeholder for training code
    # should return the path to the trained model
    return None
