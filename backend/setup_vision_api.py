#!/usr/bin/env python3
"""
Quick setup script for Google Cloud Vision API Product Search

This script helps you set up the Product Set for Q-CODE product search.
Run this ONCE after creating your Google Cloud project and service account.
"""

import os
from google.cloud import vision
from dotenv import load_dotenv

load_dotenv()

def create_product_set():
    """Create a Product Set for Q-CODE products"""
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
    location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-east1')
    product_set_id = os.getenv('GOOGLE_CLOUD_PRODUCT_SET_ID', 'qcode-product-set')

    if not project_id:
        print("[X] ERROR: GOOGLE_CLOUD_PROJECT_ID not set in .env")
        print("Please add your Google Cloud project ID to .env file")
        return False

    try:
        client = vision.ProductSearchClient()

        # Create Product Set
        product_set = vision.ProductSet(
            display_name="Q-CODE Products"
        )

        location_path = f"projects/{project_id}/locations/{location}"

        print(f"Creating Product Set in {location_path}...")

        response = client.create_product_set(
            parent=location_path,
            product_set=product_set,
            product_set_id=product_set_id
        )

        print(f"[OK] Product Set created successfully!")
        print(f"   Name: {response.name}")
        print(f"   Display Name: {response.display_name}")
        print()
        print("[*] Setup complete! You can now register products.")

        return True

    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"[OK] Product Set '{product_set_id}' already exists")
            print("   No action needed. You can start registering products.")
            return True
        else:
            print(f"[X] Error creating Product Set: {e}")
            print()
            print("Troubleshooting:")
            print("1. Check that Vision API is enabled in Google Cloud Console")
            print("2. Verify service account has 'Cloud Vision Admin' role")
            print("3. Ensure GOOGLE_APPLICATION_CREDENTIALS points to valid JSON file")
            return False

def verify_credentials():
    """Verify Google Cloud credentials are set up correctly"""
    print("[*] Verifying Google Cloud setup...\n")

    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')

    if not creds_path:
        print("[X] GOOGLE_APPLICATION_CREDENTIALS not set")
        return False

    if not os.path.exists(creds_path):
        print(f"[X] Credentials file not found: {creds_path}")
        return False

    print(f"[OK] Credentials file found: {creds_path}")

    if not project_id:
        print("[X] GOOGLE_CLOUD_PROJECT_ID not set")
        return False

    print(f"[OK] Project ID: {project_id}")

    return True

def main():
    print("=" * 60)
    print("  Google Cloud Vision API Product Search Setup")
    print("  Q-ProcureAssistant")
    print("=" * 60)
    print()

    if not verify_credentials():
        print()
        print("Please complete the setup steps in VISION_API_SETUP.md")
        return

    print()
    if create_product_set():
        print()
        print("[*] All done! Your backend is ready to use Vision API Product Search")
        print()
        print("Next steps:")
        print("1. Start the backend server: uvicorn app.main:app --reload")
        print("2. Register products via /api/products endpoint")
        print("3. Search for similar products via /api/analyze-image endpoint")
    else:
        print()
        print("[X] Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
