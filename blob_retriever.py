import os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# Define your storage account URL
account_url = "https://<YOUR STORAGE ACCOUNT NAME>.blob.core.windows.net"

# Use DefaultAzureCredential for authentication
default_credential = DefaultAzureCredential()

# Create the BlobServiceClient object
blob_service_client = BlobServiceClient(account_url, credential=default_credential)

# Specify the container name
container_name = "<YOUR CONTAINER>"

# Define the prefix to filter blobs by the directory structure
prefix = "<YOUR PREFIX>"

# Create a local directory to store downloaded files
local_download_path = "././static/images"
if not os.path.exists(local_download_path):
    os.makedirs(local_download_path)

# Function to download a blob to a file path
def download_blob_to_file(blob_service_client, container_name, blob_name, download_file_path):
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    with open(file=download_file_path, mode="wb") as download_file:
        download_stream = blob_client.download_blob()
        download_file.write(download_stream.readall())

# Get the container client
container_client = blob_service_client.get_container_client(container_name)

# List blobs in the container with the specified prefix
blob_list = container_client.list_blobs(name_starts_with=prefix)

print("\nDownloading JPG blobs:")
for blob in blob_list:
    # Check if the blob name ends with .jpg and is directly within the prefix directory
    if blob.name.lower().endswith('.jpg'):
        # Remove the prefix from the blob name
        relative_path = blob.name[len(prefix):]
        # Check if there are no further slashes in the relative path
        if '/' not in relative_path:
            # Download the blob
            download_file_path = os.path.join(local_download_path, relative_path)
            print(f"Downloading {blob.name} to {download_file_path}")
            download_blob_to_file(blob_service_client, container_name, blob.name, download_file_path)
            print(f" - {blob.name} downloaded successfully.")
