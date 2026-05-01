from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.core.exceptions import AzureError
from config import Config
import os

class AzureBlobManager:
    def __init__(self):
        self.connection_string = Config.AZURE_STORAGE_CONNECTION_STRING
        self.container_name = Config.AZURE_CONTAINER_NAME
        self.client = None
        
        if self.connection_string:
            try:
                self.client = BlobServiceClient.from_connection_string(self.connection_string)
                self._ensure_container()
            except Exception as e:
                print(f"Azure Storage Init Warning: {e}. Falling back to local storage.")

    def _ensure_container(self):
        try:
            container_client = self.client.get_container_client(self.container_name)
            if not container_client.exists():
                container_client.create_container()
        except AzureError:
            pass

    def upload(self, file_content, filename, content_type):
        """Uploads to Azure Blob or Local Filesystem depending on config."""
        if not self.client:
            # Local filesystem upload for VM/Docker volume persistence
            local_path = os.path.join(Config.LOCAL_UPLOADS_DIR, filename)
            os.makedirs(Config.LOCAL_UPLOADS_DIR, exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(file_content)
            # Return relative path for local access
            return f"/data/uploads/{filename}"

        try:
            blob_client = self.client.get_blob_client(container=self.container_name, blob=filename)
            blob_client.upload_blob(
                file_content, 
                overwrite=True, 
                content_settings=ContentSettings(content_type=content_type)
            )
            return blob_client.url
        except AzureError as e:
            print(f"Cloud upload failed, check connection: {e}")
            return None

blob_manager = AzureBlobManager()
