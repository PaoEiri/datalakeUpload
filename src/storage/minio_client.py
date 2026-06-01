import io
import logging
from typing import Optional

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class MinioClient:
    def __init__(
        self,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        secure: bool = False,
    ) -> None:
        self.bucket_name = bucket_name
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
            use_ssl=secure,
        )

    def ensure_bucket(self, bucket_name: Optional[str] = None) -> None:
        bucket_name = bucket_name or self.bucket_name
        try:
            self.client.head_bucket(Bucket=bucket_name)
        except ClientError:
            self.client.create_bucket(Bucket=bucket_name)
            logger.info("Created MinIO bucket %s", bucket_name)

    def upload_fileobj(self, fileobj: io.BufferedIOBase, object_name: str, bucket_name: Optional[str] = None) -> None:
        bucket_name = bucket_name or self.bucket_name
        fileobj.seek(0)
        self.client.upload_fileobj(fileobj, bucket_name, object_name)

    def get_object(self, object_name: str, bucket_name: Optional[str] = None, byte_range: Optional[str] = None):
        bucket_name = bucket_name or self.bucket_name
        kwargs = {"Bucket": bucket_name, "Key": object_name}
        if byte_range:
            kwargs["Range"] = byte_range
        return self.client.get_object(**kwargs)

    def exists(self, object_name: str, bucket_name: Optional[str] = None) -> bool:
        bucket_name = bucket_name or self.bucket_name
        try:
            self.client.head_object(Bucket=bucket_name, Key=object_name)
            return True
        except ClientError:
            return False

    def read_bytes(self, object_name: str, bucket_name: Optional[str] = None) -> bytes:
        response = self.get_object(object_name, bucket_name=bucket_name)
        return response["Body"].read()

    def download_fileobj(self, object_name: str, fileobj: io.BufferedIOBase, bucket_name: Optional[str] = None) -> None:
        bucket_name = bucket_name or self.bucket_name
        self.client.download_fileobj(bucket_name, object_name, fileobj)
