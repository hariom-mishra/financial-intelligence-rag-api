from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from core import aws_setup
from core.security import get_current_user
from schema.users import Users
from worker.queue import enqueue_document_processing

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/doc/")
async def upload_file(
    file: UploadFile = File(...),
    current_user: Users = Depends(get_current_user),
    s3_client=Depends(aws_setup.get_s3_session),
):
    """
    Upload a PDF document to S3 under the authenticated user's namespace
    (s3://<bucket>/<user_id>/<filename>), then enqueue a background
    Redis job to parse, chunk, and index it into the user's Qdrant collection.
    """
    # Namespace the S3 key by user_id so documents stay isolated
    s3_key = f"{current_user.id}/{file.filename}"

    try:
        await s3_client.upload_fileobj(
            file.file,
            aws_setup.BUCKET_NAME,
            s3_key,
            ExtraArgs={"ContentType": file.content_type},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}")

    # Dispatch background processing job via Redis Queue
    job = enqueue_document_processing(user_id=current_user.id, s3_key=s3_key)

    return {
        "status": "processing",
        "filename": file.filename,
        "s3_key": s3_key,
        "job_id": job.id,
        "message": "File uploaded. Indexing is running in the background.",
    }