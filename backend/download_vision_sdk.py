#!/usr/bin/env python3
"""
Download Vision AI SDK from Google Cloud Storage
"""
import os
from google.cloud import storage

def download_vision_sdk():
    """Download visionai SDK wheel file from GCS"""
    try:
        # Initialize storage client
        client = storage.Client()

        # Get bucket
        bucket = client.bucket('visionai-artifacts')

        # Download file
        blob = bucket.blob('visionai-0.0.6-py3-none-any.whl')
        blob.download_to_filename('visionai-0.0.6-py3-none-any.whl')

        print("✓ Vision AI SDK downloaded successfully")
        print("  File: visionai-0.0.6-py3-none-any.whl")

        return True

    except Exception as e:
        print(f"✗ Failed to download Vision AI SDK: {e}")
        print()
        print("Alternative: Download manually from browser")
        print("URL: https://storage.googleapis.com/visionai-artifacts/visionai-0.0.6-py3-none-any.whl")
        return False

if __name__ == "__main__":
    download_vision_sdk()
