from fastapi import APIRouter, UploadFile, File

router = APIRouter(prefix="/upload", tags=["upload"])

#upload file
@router.post("/doc/")
async def upload_file(file: UploadFile = File(...)):
    return {
        "status": "received",
        "filename": file.filename,
        "content_type": file.content_type
    }