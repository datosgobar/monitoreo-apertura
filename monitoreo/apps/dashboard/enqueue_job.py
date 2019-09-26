from django_rq import get_queue


def enqueue_job_with_timeout(queue_name, function, timeout, args=None, kwargs=None):
    get_queue(queue_name).enqueue_call(function, args, kwargs, timeout=timeout)
