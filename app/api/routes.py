from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/")



#upload file
@router.post("/upload")
def upload_file():
    pass


#ask
@router.get("/")
def ask_question():
    pass

