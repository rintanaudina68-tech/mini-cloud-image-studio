import boto3
from botocore.exceptions import BotoCoreError, ClientError
from typing import List, Dict, Any, Optional, Tuple
from config.settings import settings

class S3Service:
    """Service wrapper for S3 Object Storage via Boto3."""

    def __init__(self):
        self.bucket_name = settings.S3_BUCKET_NAME
        self.endpoint_url = settings.S3_ENDPOINT_URL
        self._client = None

    def get_client(self):
        """Lazy initialization of the Boto3 S3 client."""
        if self._client is None:
            self._client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
        return self._client

    def check_connection(self) -> Tuple[bool, str]:
        """Verify network connectivity and response from the local S3 endpoint."""
        try:
            client = self.get_client()
            client.list_buckets()
            return True, "Connected to S3 Endpoint"
        except (ClientError, BotoCoreError, Exception) as e:
            return False, f"Failed to connect to S3 ({self.endpoint_url}): {str(e)}"

    def ensure_bucket_exists(self) -> Tuple[bool, str]:
        """Check if S3 bucket exists; create automatically if not available."""
        try:
            client = self.get_client()
            response = client.list_buckets()
            existing_buckets = [b["Name"] for b in response.get("Buckets", [])]

            if self.bucket_name not in existing_buckets:
                # Create bucket
                if settings.AWS_REGION == "us-east-1":
                    client.create_bucket(Bucket=self.bucket_name)
                else:
                    client.create_bucket(
                        Bucket=self.bucket_name,
                        CreateBucketConfiguration={"LocationConstraint": settings.AWS_REGION}
                    )
                return True, f"Bucket '{self.bucket_name}' created successfully."
            return True, f"Bucket '{self.bucket_name}' is available."
        except Exception as e:
            return False, f"S3 Bucket Initialization Error: {str(e)}"

    def upload_image(self, file_bytes: bytes, object_key: str, content_type: str = "image/png") -> Tuple[bool, str]:
        """Upload image bytes to S3 object storage."""
        try:
            client = self.get_client()
            client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=file_bytes,
                ContentType=content_type
            )
            return True, f"Successfully uploaded object '{object_key}' to S3."
        except Exception as e:
            return False, f"Failed to upload image to S3: {str(e)}"

    def download_image(self, object_key: str) -> Tuple[Optional[bytes], str]:
        """Download raw image bytes from S3 by object key."""
        try:
            client = self.get_client()
            response = client.get_object(Bucket=self.bucket_name, Key=object_key)
            content = response["Body"].read()
            return content, "Success"
        except Exception as e:
            return None, f"Failed to download object '{object_key}': {str(e)}"

    def delete_image(self, object_key: str) -> Tuple[bool, str]:
        """Delete image object from S3 storage."""
        try:
            client = self.get_client()
            client.delete_object(Bucket=self.bucket_name, Key=object_key)
            return True, f"Object '{object_key}' deleted from S3."
        except Exception as e:
            return False, f"Failed to delete object '{object_key}': {str(e)}"

    def list_images(self) -> Tuple[List[Dict[str, Any]], str]:
        """List all image objects present in the S3 bucket."""
        try:
            client = self.get_client()
            response = client.list_objects_v2(Bucket=self.bucket_name)
            contents = response.get("Contents", [])
            images = []
            for item in contents:
                images.append({
                    "object_key": item["Key"],
                    "file_size": item["Size"],
                    "last_modified": item["LastModified"].isoformat()
                })
            return images, "Success"
        except Exception as e:
            return [], f"Failed to list S3 objects: {str(e)}"

# Global Service Singleton
s3_service = S3Service()
