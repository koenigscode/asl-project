import time
from myapp.models import TrainingJob
from myapp.shared_state import get_event


def testTraining(job_id):
    """Simulate long-running process and check for stop signal."""
    i = 0
    job = TrainingJob.objects.get(id=job_id)
    while i < 100000000:
        i += 1
        print("test: " + str(i))
        time.sleep(1)
        print("test: " + str(get_event(job_id).is_set()))
        if get_event(job_id).is_set():
            break
        


    # This step of checking will be necessary in the actual implementation
    if not get_event(job_id).is_set():
        job.status = 'COMPLETED'
        job.save()
        print("job completed")
    else:
        print("job stopped")
        get_event(job_id).clear()