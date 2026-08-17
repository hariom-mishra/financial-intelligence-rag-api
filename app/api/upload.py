from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from core import aws_setup

router = APIRouter(prefix="/upload", tags=["upload"])

#upload file
@router.post("/doc/")
async def upload_file(
    file: UploadFile = File(...),
    s3_client = Depends(aws_setup.get_s3_session)
):
    try: 
        await s3_client.upload_fileobj(
            file.file,
            aws_setup.BUCKET_NAME,
            file.filename,
            ExtraArgs={"ContentType": file.content_type}
        )
        return {
            "status": "received",
            "filename": file.filename,
            "content_type": file.content_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))