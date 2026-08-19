"""
Redis Queue setup.

Usage:
    from worker.queue import enqueue_document_processing
    job = enqueue_document_processing(user_id=1, s3_key="1/report.pdf")
"""
import redis
from rq import Queue
from core.setttings import settings

# Synchronous Redis connection used by rq (rq does not use asyncio)
_redis_conn = redis.from_url(settings.REDIS_URL)

# Default queue — workers listen on this queue
document_queue = Queue("documents", connection=_redis_conn)


def enqueue_document_processing(user_id: int, s3_key: str):
    """
    Push a document-processing job onto the Redis queue.

    Returns the rq Job object (contains job.id for status tracking).
    """
    from worker.tasks import process_document_task  # lazy import avoids circular deps

    job = document_queue.enqueue(
        process_document_task,
        user_id,
        s3_key,
        job_timeout=600,  # 10 minutes max
    )
    return job
