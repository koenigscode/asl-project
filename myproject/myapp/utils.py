import torch
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
    # Retrieve the TrainingJob instance
    print("Training model with ID:", training_job_id)
    training_job = TrainingJob.objects.get(id=training_job_id)
    training_job.status = 'In Progress'
    training_job.save()

    # Load the dataset
    dataset_path = os.path.join(settings.MEDIA_ROOT, 'datasets', training_job.dataset.name)
    # Implement dataset loading logic here

    # Extract hyperparameters
    hyperparameters = training_job.hyperparameters
    num_epochs = hyperparameters.get('num_epochs', 10)
    learning_rate = hyperparameters.get('learning_rate', 0.001)

    # Add other hyperparameters as needed

    # Initialize or load the model
    if training_job.base_model:
        # Load the pre-trained model
        base_model_path = training_job.base_model.model_file.path
        model = torch.load(base_model_path, weights_only=True)
        print("Loaded model path:", base_model_path)
    else:
        # Initialize a new model
        raise NotImplementedError("Model from scratch initialization logic is not implemented yet")

    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    # Training loop
    for epoch in range(1, num_epochs + 1):
        # Training logic per epoch
        model.train()
        epoch_loss = 0.0
        correct = 0
        total = 0

        # Iterate over data loader
        for inputs, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            # Update statistics
            epoch_loss += loss.item()
            # Calculate accuracy
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        # Calculate average loss and accuracy
        avg_loss = epoch_loss / len(train_loader)
        accuracy = 100 * correct / total

        # Save metrics to the database
        TrainingMetrics.objects.create(
            job=training_job,
            epoch=epoch,
            loss=avg_loss,
            accuracy=accuracy
        )

        # Optional: Early stopping or interruption logic
        if should_stop_training():
            training_job.status = 'Stopped'
            training_job.save()
            break

    else:
        # Training completed all epochs
        training_job.status = 'Completed'
        training_job.completed_at = timezone.now()
        training_job.save()

    # Save the trained model
    output_model_name = f"model_{training_job.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}"
    output_model_path = os.path.join(settings.MEDIA_ROOT, 'trained_models', output_model_name + '.pt')
    torch.save(model.state_dict(), output_model_path)

    # Create a TrainedModel instance
    trained_model = TrainedModel.objects.create(
        name=output_model_name,
        model_file=output_model_path
    )

    # Link the output model to the training job
    training_job.output_model = trained_model
    training_job.save()
