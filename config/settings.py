import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if available
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

class AppSettings:
    """Application Settings and Configuration Management."""
    
    # Application Info
    APP_NAME: str = "Mini Cloud Image Studio"
    APP_VERSION: str = "1.0.0"
    DEVELOPER_ROLE: str = "Senior Cloud Engineer & Full-Stack Developer"

    # AWS Mock / Local Credentials
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "mock_access_key")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "mock_secret_key")
    AWS_REGION: str = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION", "us-east-1"))

    # Local Cloud Service Endpoints
    S3_ENDPOINT_URL: str = os.getenv("S3_ENDPOINT_URL", "http://localhost:9000")
    DYNAMODB_ENDPOINT_URL: str = os.getenv("DYNAMODB_ENDPOINT_URL", "http://localhost:8000")

    # Cloud Storage & Database Entity Names
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "mini-cloud-image-studio")
    DYNAMODB_TABLE_NAME: str = os.getenv("DYNAMODB_TABLE_NAME", "MiniCloudImages")

    # Supported Image Formats
    ALLOWED_EXTENSIONS: set = {"png", "jpg", "jpeg", "webp"}
    MAX_FILE_SIZE_MB: int = 10

settings = AppSettings()
