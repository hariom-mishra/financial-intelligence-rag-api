"""
Background task executed by the rq worker process.

Run the worker with:
    cd app && rq worker documents --with-scheduler
"""
import asyncio
import tempfile
from pathlib import Path
import logging
from core.aws_setup import session
from services.chunking_services import document_chunk
from services.qdrant_services import index_documents
from core.setttings import settings

logger = logging.getLogger(__name__)


def process_document_task(user_id: int, s3_key: str) -> dict:
    """
    rq entry point (synchronous wrapper around the async pipeline).

    Steps:
      1. Download the file from S3 to a temp file.
      2. Parse + chunk the PDF via docling / langchain splitters.
      3. Upsert chunks into the user's Qdrant collection.

    Returns a dict with status info.
    """
    return asyncio.run(_async_process_document(user_id, s3_key))


async def _async_process_document(user_id: int, s3_key: str) -> dict:
    collection_name = f"user_{user_id}_docs"
    logger.info(f"[Worker] Processing s3://{settings.S3_BUCKET_NAME}/{s3_key} → {collection_name}")

    # --- 1. Download from S3 ---
    suffix = Path(s3_key).suffix or ".pdf"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        async with session.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        ) as s3:
            await s3.download_file(settings.S3_BUCKET_NAME, s3_key, str(tmp_path))

        logger.info(f"[Worker] Downloaded to {tmp_path}")

        # --- 2. Parse + chunk ---
        chunks = document_chunk(file_path=str(tmp_path))
        logger.info(f"[Worker] Produced {len(chunks)} chunks")

        # --- 3. Upsert into Qdrant ---
        await index_documents(user_id=user_id, chunks=chunks)

        logger.info(f"[Worker] Indexed {len(chunks)} chunks into {collection_name}")
        return {"status": "success", "chunks_indexed": len(chunks), "collection": collection_name}

    finally:
        # Clean up temp file
        if tmp_path.exists():
            tmp_path.unlink()
