import os
from io import BytesIO
from azure.storage.blob import BlobServiceClient
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/v1/azure_blob", tags=["Azure Blob Storage"])

# Azure Blob Storage credentials - replace this with your actual connection string
AZURE_STORAGE_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=sa01fastapidev;AccountKey=NYzl5Vmxrdi4GVaGCz6Zm7IyewyX7SOFd2jYbpJ3au8EDSOp5KmJTHSe4YLjv2F5T9AwmuKnBw80+ASt5vCLEg==;EndpointSuffix=core.windows.net"

# Create the BlobServiceClient object using the connection string
blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

# Optionally, set a default container name (you can also pass it dynamically later)
DEFAULT_CONTAINER_NAME = "test-container"

# Function to create a container if it doesn't exist
def create_container_if_not_exists(container_name: str):
    container_client = blob_service_client.get_container_client(container_name)
    if not container_client.exists():
        container_client.create_container()
    return container_client

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...), container_name: str = DEFAULT_CONTAINER_NAME):
    try:
        # Create or get the container
        container_client = create_container_if_not_exists(container_name)

        # Create blob client for the file
        blob_client = container_client.get_blob_client(file.filename)

        # Upload the file to the Azure Blob
        blob_client.upload_blob(file.file, overwrite=True)
        return {"message": f"File {file.filename} uploaded successfully to container {container_name}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/download/{file_name}")
async def download_file(file_name: str, container_name: str = DEFAULT_CONTAINER_NAME):
    try:
        # Create or get the container
        container_client = create_container_if_not_exists(container_name)

        # Create blob client for the file
        blob_client = container_client.get_blob_client(file_name)

        # Download the file
        download_stream = blob_client.download_blob()
        file_data = download_stream.readall()

        # Return the file as a StreamingResponse
        return StreamingResponse(BytesIO(file_data), media_type="application/octet-stream", headers={"Content-Disposition": f"attachment; filename={file_name}"})
    except Exception:
        raise HTTPException(status_code=404, detail="File not found")

@router.get("/list/")
async def list_blobs(container_name: str = DEFAULT_CONTAINER_NAME):
    try:
        # Create or get the container
        container_client = create_container_if_not_exists(container_name)

        # List blobs in the container
        blob_list = container_client.list_blobs()
        blobs = [blob.name for blob in blob_list]
        return {"blobs": blobs}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))