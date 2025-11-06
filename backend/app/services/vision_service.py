import os
from google.cloud import vision
from google.cloud import storage
from typing import Dict, List
from dotenv import load_dotenv
import uuid

load_dotenv()

def get_vision_client():
    """Get Google Vision API ProductSearchClient"""
    # Set credentials path
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if credentials_path and os.path.exists(credentials_path):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    return vision.ProductSearchClient()

def get_image_annotator_client():
    """Get Google Vision API ImageAnnotatorClient"""
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if credentials_path and os.path.exists(credentials_path):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    return vision.ImageAnnotatorClient()

def get_storage_client():
    """Get Google Cloud Storage client"""
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if credentials_path and os.path.exists(credentials_path):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    return storage.Client()

def upload_to_gcs(local_file_path: str, destination_blob_name: str = None) -> str:
    """
    Upload file to Google Cloud Storage

    Returns:
        GCS URI (gs://bucket/file.jpg)
    """
    try:
        bucket_name = os.getenv('GOOGLE_CLOUD_STORAGE_BUCKET')
        if not bucket_name:
            raise ValueError("GOOGLE_CLOUD_STORAGE_BUCKET not set")

        storage_client = get_storage_client()
        bucket = storage_client.bucket(bucket_name)

        # Generate unique blob name if not provided
        if not destination_blob_name:
            ext = os.path.splitext(local_file_path)[1]
            destination_blob_name = f"products/{uuid.uuid4()}{ext}"

        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(local_file_path)

        gcs_uri = f"gs://{bucket_name}/{destination_blob_name}"
        return gcs_uri

    except Exception as e:
        print(f"Failed to upload to GCS: {e}")
        raise

def search_similar_products_vision(image_path: str, product_set_id: str = None) -> Dict:
    """
    Search for similar products using Google Vision API Product Search

    Args:
        image_path: Path to the query image
        product_set_id: Full product set path (if None, uses default from env)

    Returns:
        Dictionary with similar products and scores
    """
    try:
        # Get both clients
        search_client = get_vision_client()
        image_client = get_image_annotator_client()

        project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-east1')
        product_set_name = os.getenv('GOOGLE_CLOUD_PRODUCT_SET_ID', 'qcode-product-set')

        # Read image file
        with open(image_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        # Build product set path
        if not product_set_id:
            product_set_id = search_client.product_set_path(
                project=project_id,
                location=location,
                product_set=product_set_name
            )

        # Product search parameters
        product_search_params = vision.ProductSearchParams(
            product_set=product_set_id,
            product_categories=['general-v1'],
            filter=''  # Can add filters like "color=red"
        )

        image_context = vision.ImageContext(
            product_search_params=product_search_params
        )

        # Perform product search
        response = image_client.product_search(
            image=image,
            image_context=image_context
        )

        results = []

        # Process grouped results
        for result in response.results:
            product = result.product
            score = result.score  # Similarity score (0-1)

            # Extract product ID from full path
            product_id = product.name.split('/')[-1]

            # Get product labels
            labels = {}
            for label in product.product_labels:
                labels[label.key] = label.value

            results.append({
                'product_id': product_id,
                'display_name': product.display_name,
                'description': product.description,
                'similarity': round(score * 100, 1),  # Convert to 0-100
                'labels': labels,
                'product_category': product.product_category
            })

        # Sort by similarity (highest first)
        results.sort(key=lambda x: x['similarity'], reverse=True)

        return {
            'success': True,
            'similar_products': results,
            'method': 'google_vision_product_search',
            'total_results': len(results)
        }

    except Exception as e:
        print(f"Vision API Product Search error: {e}")
        return {
            'success': False,
            'error': str(e),
            'similar_products': [],
            'fallback_available': True
        }

def create_product_in_vision(
    product_id: str,
    display_name: str,
    description: str,
    image_path: str,
    category: str = 'general-v1',
    product_labels: Dict = None
) -> Dict:
    """
    Register a new product in Google Vision API Product Search

    Steps:
    1. Upload image to Google Cloud Storage
    2. Create product in Vision API
    3. Add reference image to product
    4. Add product to product set

    Args:
        product_id: Unique product ID (e.g., Q-CODE)
        display_name: Product name
        description: Product description
        image_path: Local path to product image
        category: Product category (default: 'general-v1')
        product_labels: Dict of key-value labels (e.g., {'material': 'steel'})

    Returns:
        Success status and product info
    """
    try:
        client = get_vision_client()
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-east1')
        product_set_name = os.getenv('GOOGLE_CLOUD_PRODUCT_SET_ID', 'qcode-product-set')

        # Step 1: Upload image to Google Cloud Storage
        print(f"Uploading image to GCS: {image_path}")
        gcs_uri = upload_to_gcs(image_path, f"products/{product_id}.jpg")
        print(f"Image uploaded: {gcs_uri}")

        # Step 2: Create product labels
        labels = []
        if product_labels:
            for key, value in product_labels.items():
                labels.append(
                    vision.Product.KeyValue(key=key, value=str(value))
                )

        # Step 3: Create product
        product = vision.Product(
            display_name=display_name,
            description=description,
            product_category=category,
            product_labels=labels
        )

        location_path = client.location_path(project=project_id, location=location)

        print(f"Creating product in Vision API: {product_id}")
        created_product = client.create_product(
            parent=location_path,
            product=product,
            product_id=product_id
        )
        print(f"Product created: {created_product.name}")

        # Step 4: Add reference image
        reference_image = vision.ReferenceImage(uri=gcs_uri)

        print(f"Adding reference image: {gcs_uri}")
        image_response = client.create_reference_image(
            parent=created_product.name,
            reference_image=reference_image,
            reference_image_id=f"{product_id}-ref-image"
        )
        print(f"Reference image added: {image_response.name}")

        # Step 5: Add product to product set
        product_set_path = client.product_set_path(
            project=project_id,
            location=location,
            product_set=product_set_name
        )

        print(f"Adding product to product set: {product_set_path}")
        client.add_product_to_product_set(
            name=product_set_path,
            product=created_product.name
        )
        print(f"Product added to product set")

        return {
            'success': True,
            'product_name': created_product.name,
            'product_id': product_id,
            'display_name': created_product.display_name,
            'gcs_uri': gcs_uri,
            'reference_image': image_response.name
        }

    except Exception as e:
        print(f"Failed to create product in Vision API: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e)
        }

def simple_image_similarity_vision(image1_path: str, image2_path: str) -> Dict:
    """
    Simple image similarity using Vision API label detection
    Fallback method when Product Search is not configured
    """
    try:
        client = get_vision_client()

        # Analyze both images
        with open(image1_path, 'rb') as f1:
            image1 = vision.Image(content=f1.read())
        with open(image2_path, 'rb') as f2:
            image2 = vision.Image(content=f2.read())

        # Get labels for both images
        response1 = client.label_detection(image=image1)
        response2 = client.label_detection(image=image2)

        labels1 = {label.description: label.score for label in response1.label_annotations}
        labels2 = {label.description: label.score for label in response2.label_annotations}

        # Calculate similarity based on common labels
        common_labels = set(labels1.keys()) & set(labels2.keys())

        if not common_labels:
            similarity = 0
        else:
            # Average score of common labels
            similarity = sum(
                min(labels1[label], labels2[label]) for label in common_labels
            ) / len(common_labels) * 100

        return {
            'success': True,
            'similarity': round(similarity, 1),
            'common_labels': list(common_labels),
            'method': 'vision_label_detection'
        }

    except Exception as e:
        print(f"Vision API error: {e}")
        return {
            'success': False,
            'similarity': 0,
            'error': str(e)
        }

def detect_labels_and_objects(image_path: str) -> Dict:
    """
    Detect labels and objects in image using Vision API
    Useful for product categorization
    """
    try:
        client = get_vision_client()

        with open(image_path, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        # Perform label detection
        label_response = client.label_detection(image=image)
        labels = [
            {
                'description': label.description,
                'score': round(label.score * 100, 1),
                'confidence': label.score
            }
            for label in label_response.label_annotations
        ]

        # Perform object detection
        object_response = client.object_localization(image=image)
        objects = [
            {
                'name': obj.name,
                'score': round(obj.score * 100, 1)
            }
            for obj in object_response.localized_object_annotations
        ]

        return {
            'success': True,
            'labels': labels,
            'objects': objects
        }

    except Exception as e:
        print(f"Vision API error: {e}")
        return {
            'success': False,
            'error': str(e),
            'labels': [],
            'objects': []
        }
