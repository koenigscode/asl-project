"""
File: shared_state.py
Description: Source code which allows the different threads in the admin UI to communicate.

Contributors:
David Schoen

Created: 2024-12-15
Last Modified: 2024-12-15

Project: A Sign From Above
URL: https://git.chalmers.se/courses/dit826/2024/group4

License: MIT License (see LICENSE file for details)
"""

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
