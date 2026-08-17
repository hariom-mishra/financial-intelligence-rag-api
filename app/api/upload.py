from fastapi import APIRouter

router = APIRouter(prefix="/upload", tags=["upload"])

#upload file
@router.post("/doc/")
def upload_file():
    pass