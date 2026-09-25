from typing import Optional
import boto3
from botocore.exceptions import ClientError
import structlog
from app.core.config import settings

logger = structlog.get_logger(__name__)


class S3StorageProvider:
    """Storage provider implementation for AWS S3."""

    def __init__(self):
        self.bucket = settings.S3_BUCKET
        self.enabled = bool(self.bucket and settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY)

    def _get_client(self):
        if not self.enabled:
            return None
        return boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )

    def upload(self, file_obj, key: str, content_type: Optional[str] = None) -> bool:
        client = self._get_client()
        if not client:
            logger.warning("S3 client unconfigured, skipping upload", key=key)
            return False

        try:
            extra_args = {}
            if content_type:
                extra_args["ContentType"] = content_type

            client.upload_fileobj(file_obj, self.bucket, key, ExtraArgs=extra_args)
            logger.info("File uploaded to S3", key=key, bucket=self.bucket)
            return True
        except ClientError as exc:
            logger.error("Error uploading file to S3", key=key, error=str(exc))
            return False

    def delete(self, key: str) -> bool:
        client = self._get_client()
        if not client:
            return False

        try:
            client.delete_object(Bucket=self.bucket, Key=key)
            logger.info("File deleted from S3", key=key)
            return True
        except ClientError as exc:
            logger.error("Error deleting file from S3", key=key, error=str(exc))
            return False

    def get_url(self, key: str, expiration: int = 3600) -> Optional[str]:
        client = self._get_client()
        if not client:
            return None

        try:
            url = client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expiration,
            )
            return url
        except ClientError as exc:
            logger.error("Error generating presigned URL", key=key, error=str(exc))
            return None
