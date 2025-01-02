# shared_state.py
from threading import Event

# Dictionary to store stop events for different jobs
job_events = {}

def get_event(job_id):
    """Get or create an event for a specific job ID."""
    if job_id not in job_events:
        job_events[job_id] = Event()
    return job_events[job_id]
    
def clear_event(job_id):
    """Clear the stop event for a job."""
    if job_id in job_events:
        del job_events[job_id]
