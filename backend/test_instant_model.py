"""
Roboflow Instant Model Specific Test
Instant 모델에 특화된 테스트
"""
import os
import sys
import requests
from dotenv import load_dotenv

# UTF-8 출력 강제
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
TEST_IMAGE = "../aws_bedrock/testcan.jpg"

# 확인된 정보
PROJECT_ID = "hackerthon2025-fnd8v-instant-2"
VERSION = "2"

print("="*80)
print("Roboflow Instant Model Test")
print("="*80)
print(f"\nConfirmed Information:")
print(f"   Project ID: {PROJECT_ID}")
print(f"   Version: {VERSION}")
print(f"   Model ID: {PROJECT_ID}/{VERSION}")
print(f"   API Key: {ROBOFLOW_API_KEY[:10]}...{ROBOFLOW_API_KEY[-4:]}")
print(f"   Test Image: {TEST_IMAGE}")

# 테스트할 엔드포인트들
endpoints = [
    # 1. 일반 Object Detection 엔드포인트
    {
        "name": "Standard detect.roboflow.com",
        "url": f"https://detect.roboflow.com/{PROJECT_ID}/{VERSION}",
        "method": "multipart"
    },
    # 2. Serverless 엔드포인트
    {
        "name": "Serverless API",
        "url": f"https://serverless.roboflow.com/{PROJECT_ID}/{VERSION}",
        "method": "multipart"
    },
    # 3. Outline (Instance Segmentation용이지만 시도)
    {
        "name": "Outline API (segmentation)",
        "url": f"https://outline.roboflow.com/{PROJECT_ID}/{VERSION}",
        "method": "multipart"
    },
    # 4. Inference 엔드포인트
    {
        "name": "Infer endpoint",
        "url": f"https://infer.roboflow.com/{PROJECT_ID}/{VERSION}",
        "method": "multipart"
    },
]

print("\n" + "="*80)
print("Testing Different Endpoints")
print("="*80)

for i, endpoint in enumerate(endpoints, 1):
    print(f"\n[Test {i}/{len(endpoints)}] {endpoint['name']}")
    print(f"   URL: {endpoint['url']}")

    try:
        with open(TEST_IMAGE, "rb") as image_file:
            response = requests.post(
                endpoint['url'],
                params={"api_key": ROBOFLOW_API_KEY},
                files={"file": image_file},
                timeout=15
            )

        print(f"   Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            predictions = result.get('predictions', [])
            print(f"   [SUCCESS] {len(predictions)} objects detected!")

            if predictions:
                for pred in predictions[:3]:
                    class_name = pred.get('class', 'unknown')
                    confidence = pred.get('confidence', 0)
                    print(f"      * {class_name}: {confidence:.2%}")

            print("\n" + "="*80)
            print("SUCCESS! Working configuration found!")
            print("="*80)
            print(f"\nEndpoint: {endpoint['url']}")
            print(f"Model ID: {PROJECT_ID}/{VERSION}")
            print("\nUpdate .env file:")
            print(f"   ROBOFLOW_MODEL_ID={PROJECT_ID}/{VERSION}")
            print("\nIf using different endpoint, update roboflow_service.py:")
            print(f"   INFERENCE_URL = \"{endpoint['url'].split('/' + PROJECT_ID)[0]}\"")
            break
        else:
            error_msg = response.text[:200]
            print(f"   [FAIL] {error_msg}")

    except Exception as e:
        print(f"   [ERROR] {str(e)[:200]}")

else:
    print("\n" + "="*80)
    print("All endpoints failed")
    print("="*80)
    print("\nPossible issues:")
    print("   1. Model is still training (check Roboflow dashboard)")
    print("   2. Model training failed")
    print("   3. API key doesn't have access to this project")
    print("\nPlease check:")
    print(f"   - Visit: https://app.roboflow.com/2025-hackerthon/{PROJECT_ID}/2")
    print("   - Verify model training status")
    print("   - Check if model is 'Active' and 'Deployed'")
    print("   - Look for 'Use Model' button and copy the exact curl command")

print("\n" + "="*80)
