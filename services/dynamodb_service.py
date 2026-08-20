import boto3
from botocore.exceptions import BotoCoreError, ClientError
from typing import List, Dict, Any, Optional, Tuple
from config.settings import settings

class DynamoDBService:
    """Service wrapper for DynamoDB NoSQL database via Boto3."""

    def __init__(self):
        self.table_name = settings.DYNAMODB_TABLE_NAME
        self.endpoint_url = settings.DYNAMODB_ENDPOINT_URL
        self._resource = None
        self._client = None

    def get_resource(self):
        """Lazy initialization of DynamoDB Resource."""
        if self._resource is None:
            self._resource = boto3.resource(
                "dynamodb",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
        return self._resource

    def get_client(self):
        """Lazy initialization of DynamoDB Client."""
        if self._client is None:
            self._client = boto3.client(
                "dynamodb",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
        return self._client

    def check_connection(self) -> Tuple[bool, str]:
        """Verify network connectivity and response from local DynamoDB endpoint."""
        try:
            client = self.get_client()
            client.list_tables()
            return True, "Connected to DynamoDB Endpoint"
        except (ClientError, BotoCoreError, Exception) as e:
            return False, f"Failed to connect to DynamoDB ({self.endpoint_url}): {str(e)}"

    def ensure_table_exists(self) -> Tuple[bool, str]:
        """Check if DynamoDB table exists; create automatically if not available."""
        try:
            client = self.get_client()
            response = client.list_tables()
            existing_tables = response.get("TableNames", [])

            if self.table_name not in existing_tables:
                client.create_table(
                    TableName=self.table_name,
                    KeySchema=[
                        {"AttributeName": "image_id", "KeyType": "HASH"}  # Partition key
                    ],
                    AttributeDefinitions=[
                        {"AttributeName": "image_id", "AttributeType": "S"}
                    ],
                    ProvisionedThroughput={
                        "ReadCapacityUnits": 5,
                        "WriteCapacityUnits": 5
                    }
                )
                return True, f"DynamoDB Table '{self.table_name}' created successfully."
            return True, f"DynamoDB Table '{self.table_name}' is available."
        except Exception as e:
            return False, f"DynamoDB Table Initialization Error: {str(e)}"

    def save_image_metadata(self, metadata: Dict[str, Any]) -> Tuple[bool, str]:
        """Save or update image metadata record in DynamoDB."""
        try:
            resource = self.get_resource()
            table = resource.Table(self.table_name)
            
            # Ensure numbers are converted appropriately or stored cleanly
            item = {
                "image_id": str(metadata.get("image_id")),
                "file_name": str(metadata.get("file_name", "unknown")),
                "object_key": str(metadata.get("object_key", "")),
                "original_format": str(metadata.get("original_format", "PNG")),
                "processed_format": str(metadata.get("processed_format", "PNG")),
                "operation": str(metadata.get("operation", "Original Upload")),
                "width": int(metadata.get("width", 0)),
                "height": int(metadata.get("height", 0)),
                "file_size": int(metadata.get("file_size", 0)),
                "uploaded_at": str(metadata.get("uploaded_at", "")),
                "status": str(metadata.get("status", "Active"))
            }

            table.put_item(Item=item)
            return True, f"Metadata for '{item['image_id']}' stored successfully."
        except Exception as e:
            return False, f"Failed to save metadata to DynamoDB: {str(e)}"

    def get_image_metadata(self, image_id: str) -> Tuple[Optional[Dict[str, Any]], str]:
        """Retrieve single image metadata record by image_id."""
        try:
            resource = self.get_resource()
            table = resource.Table(self.table_name)
            response = table.get_item(Key={"image_id": image_id})
            item = response.get("Item")
            if item:
                return item, "Success"
            return None, f"Image metadata not found for ID: {image_id}"
        except Exception as e:
            return None, f"Failed to fetch metadata from DynamoDB: {str(e)}"

    def list_image_metadata(self) -> Tuple[List[Dict[str, Any]], str]:
        """Scan and retrieve all image metadata records from DynamoDB."""
        try:
            resource = self.get_resource()
            table = resource.Table(self.table_name)
            response = table.scan()
            items = response.get("Items", [])
            # Sort items by uploaded_at descending
            items.sort(key=lambda x: x.get("uploaded_at", ""), reverse=True)
            return items, "Success"
        except Exception as e:
            return [], f"Failed to list metadata from DynamoDB: {str(e)}"

    def delete_image_metadata(self, image_id: str) -> Tuple[bool, str]:
        """Delete image metadata record from DynamoDB by image_id."""
        try:
            resource = self.get_resource()
            table = resource.Table(self.table_name)
            table.delete_item(Key={"image_id": image_id})
            return True, f"Metadata record '{image_id}' deleted from DynamoDB."
        except Exception as e:
            return False, f"Failed to delete metadata: {str(e)}"

# Global Service Singleton
dynamodb_service = DynamoDBService()
