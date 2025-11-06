#!/usr/bin/env python3
"""
Upload product images from product_list_picture to Google Cloud Storage
"""
import os
from pathlib import Path
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()

def upload_products_to_gcs(
    source_dir: str = "../product_list_picture",
    bucket_name: str = None
):
    """
    Upload all product images to GCS

    Args:
        source_dir: Path to product_list_picture directory
        bucket_name: GCS bucket name (from .env if not provided)
    """
    if not bucket_name:
        bucket_name = os.getenv('GOOGLE_CLOUD_STORAGE_BUCKET', 'qcode-product-images')

    print(f"[*] Uploading images to gs://{bucket_name}")
    print()

    # Initialize GCS client
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # Scan product_list_picture directory
    source_path = Path(source_dir)

    if not source_path.exists():
        print(f"[X] Source directory not found: {source_path}")
        return False

    uploaded_count = 0
    skipped_count = 0

    # Iterate through Q-CODE directories
    for qcode_dir in sorted(source_path.iterdir()):
        if not qcode_dir.is_dir():
            continue

        qcode = qcode_dir.name
        print(f"[*] Processing {qcode}...")

        # Upload all images in this Q-CODE directory
        for image_file in sorted(qcode_dir.iterdir()):
            if not image_file.is_file():
                continue

            # Skip origin thumbnails
            if "origin" in image_file.name.lower():
                print(f"    [SKIP] {image_file.name} (origin thumbnail)")
                skipped_count += 1
                continue

            # Generate GCS path
            gcs_path = f"{qcode}/{image_file.name}"

            # Check if already exists
            blob = bucket.blob(gcs_path)
            if blob.exists():
                print(f"    [EXISTS] {gcs_path}")
                skipped_count += 1
                continue

            # Upload
            try:
                blob.upload_from_filename(str(image_file))
                print(f"    [OK] {gcs_path}")
                uploaded_count += 1
            except Exception as e:
                print(f"    [ERROR] {gcs_path}: {e}")

    print()
    print(f"[*] Upload complete!")
    print(f"    Uploaded: {uploaded_count} files")
    print(f"    Skipped: {skipped_count} files")
    print(f"    Bucket: gs://{bucket_name}")

    return True

if __name__ == "__main__":
    upload_products_to_gcs()
