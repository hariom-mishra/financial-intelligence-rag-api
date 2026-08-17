from core.setttings import settings
import aioboto3

session = aioboto3.Session()

async def get_s3_session():
    async with session.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    ) as s3: 
        yield s3


BUCKET_NAME= settings.S3_BUCKET_NAME