"""
Roboflow Object Detection API Comprehensive Test Script
Tests multiple model ID formats and API request methods automatically.
"""
import os
import sys
import requests
import base64
from dotenv import load_dotenv
from typing import Dict, List

# UTF-8 출력 강제
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

# 환경 변수
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
ROBOFLOW_MODEL_ID = os.getenv("ROBOFLOW_MODEL_ID")

# 테스트 이미지 경로
TEST_IMAGE = "../aws_bedrock/testcan.jpg"

# 테스트할 모델 ID 형식들
MODEL_ID_FORMATS = [
    # 참고 문서 기반 (hackerthon2025가 프로젝트명일 가능성)
    "hackerthon2025/1",
    "hackerthon2025/2",
    "hackerthon2025/3",

    # 현재 설정
    "2025-hackerthon/hackerthon2025-fnd8v-instant-2",

    # instant-2가 프로젝트명의 일부이고, 버전이 1, 2인 경우
    "hackerthon2025-fnd8v-instant-2/1",
    "hackerthon2025-fnd8v-instant-2/2",
    "hackerthon2025-fnd8v-instant-2/3",

    # instant-2가 버전 번호인 경우
    "hackerthon2025-fnd8v/instant-2",

    # 프로젝트명만 있고 버전이 숫자인 경우
    "hackerthon2025-fnd8v/1",
    "hackerthon2025-fnd8v/2",
    "hackerthon2025-fnd8v/3",

    # workspace 없이 간단한 형식
    "hackerthon2025-fnd8v-instant-2",
]


def encode_image_to_base64(image_path: str) -> str:
    """이미지를 Base64로 인코딩"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def test_method_1_multipart(model_id: str, image_path: str) -> Dict:
    """
    방식 1: multipart/form-data (현재 사용 중인 방식)
    """
    url = f"https://detect.roboflow.com/{model_id}"

    try:
        with open(image_path, "rb") as image_file:
            response = requests.post(
                url,
                params={"api_key": ROBOFLOW_API_KEY},
                files={"file": image_file},
                timeout=10
            )

        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text,
            "method": "multipart/form-data"
        }
    except Exception as e:
        return {
            "success": False,
            "status_code": None,
            "response": str(e),
            "method": "multipart/form-data"
        }


def test_method_2_base64_body(model_id: str, image_path: str) -> Dict:
    """
    방식 2: Base64 인코딩 POST body (문서 권장)
    """
    url = f"https://detect.roboflow.com/{model_id}"

    try:
        image_base64 = encode_image_to_base64(image_path)

        response = requests.post(
            url,
            params={"api_key": ROBOFLOW_API_KEY},
            data=image_base64,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )

        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text,
            "method": "base64_body"
        }
    except Exception as e:
        return {
            "success": False,
            "status_code": None,
            "response": str(e),
            "method": "base64_body"
        }


def test_method_3_url_param(model_id: str, image_url: str = None) -> Dict:
    """
    방식 3: 이미지 URL 쿼리 파라미터
    (로컬 파일은 URL로 변환 불가하므로 스킵)
    """
    if not image_url:
        return {
            "success": False,
            "status_code": None,
            "response": "No image URL provided (local file)",
            "method": "url_param"
        }

    url = f"https://detect.roboflow.com/{model_id}"

    try:
        response = requests.post(
            url,
            params={
                "api_key": ROBOFLOW_API_KEY,
                "image": image_url
            },
            timeout=10
        )

        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text,
            "method": "url_param"
        }
    except Exception as e:
        return {
            "success": False,
            "status_code": None,
            "response": str(e),
            "method": "url_param"
        }


def print_result(model_id: str, result: Dict):
    """Print test results"""
    success_icon = "[OK]" if result["success"] else "[FAIL]"

    print(f"\n{success_icon} {result['method']:<20} | Status: {result['status_code']}")

    if result["success"]:
        predictions = result["response"].get("predictions", [])
        print(f"   -> Predictions: {len(predictions)} objects detected")

        if predictions:
            for pred in predictions[:3]:
                class_name = pred.get("class", "unknown")
                confidence = pred.get("confidence", 0)
                print(f"      * {class_name}: {confidence:.2%}")
    else:
        error_msg = str(result["response"])[:200]
        print(f"   -> Error: {error_msg}")


def run_comprehensive_test():
    """Run comprehensive test"""
    print("=" * 80)
    print("Roboflow Object Detection API - Comprehensive Test")
    print("=" * 80)
    print(f"\nConfiguration:")
    print(f"   API Key: {ROBOFLOW_API_KEY[:10]}...{ROBOFLOW_API_KEY[-4:]}")
    print(f"   Current Model ID (.env): {ROBOFLOW_MODEL_ID}")
    print(f"   Test Image: {TEST_IMAGE}")
    print(f"\nTesting {len(MODEL_ID_FORMATS)} model ID formats")
    print("=" * 80)

    # Check test image
    if not os.path.exists(TEST_IMAGE):
        print(f"\n[ERROR] Test image not found: {TEST_IMAGE}")
        return

    successful_configs = []

    # Test each model ID format
    for i, model_id in enumerate(MODEL_ID_FORMATS, 1):
        print(f"\n{'='*80}")
        print(f"Test [{i}/{len(MODEL_ID_FORMATS)}] Model ID: {model_id}")
        print(f"{'='*80}")

        # Method 1: multipart/form-data
        print("\n[Method 1] multipart/form-data (current code)")
        result1 = test_method_1_multipart(model_id, TEST_IMAGE)
        print_result(model_id, result1)

        if result1["success"]:
            successful_configs.append({
                "model_id": model_id,
                "method": "multipart/form-data",
                "result": result1
            })

        # Method 2: base64 body
        print("\n[Method 2] Base64 POST body")
        result2 = test_method_2_base64_body(model_id, TEST_IMAGE)
        print_result(model_id, result2)

        if result2["success"]:
            successful_configs.append({
                "model_id": model_id,
                "method": "base64_body",
                "result": result2
            })

        # Alert on success
        if result1["success"] or result2["success"]:
            print(f"\n*** SUCCESS! This model ID works: {model_id} ***")

    # Final summary
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)

    if successful_configs:
        print(f"\n[SUCCESS] {len(successful_configs)} working configurations found!\n")

        for config in successful_configs:
            print(f"   Model ID: {config['model_id']}")
            print(f"   Method: {config['method']}")

            predictions = config['result']['response'].get('predictions', [])
            print(f"   Predictions: {len(predictions)} objects")

            if predictions:
                classes = list(set([p.get('class', 'unknown') for p in predictions]))
                print(f"   Classes: {', '.join(classes)}")

            print()

        # Recommended configuration
        print("\n" + "="*80)
        print("RECOMMENDED CONFIGURATION")
        print("="*80)
        best_config = successful_configs[0]
        print(f"\nUpdate .env file:")
        print(f"   ROBOFLOW_MODEL_ID={best_config['model_id']}")

        if best_config['method'] == 'base64_body':
            print(f"\n[WARNING] API request method needs to be changed to base64 body")
            print(f"   (Modify detect_products_in_frame function in roboflow_service.py)")
        else:
            print(f"\n[OK] Current API request method can be used as-is")

    else:
        print("\n[FAIL] No working configuration found.")
        print("\nPossible causes:")
        print("   1. All model ID formats are incorrect")
        print("   2. API key is invalid")
        print("   3. Model has not been trained yet")
        print("   4. Credits have been exhausted")
        print("\nSolutions:")
        print("   - Check exact model ID on Roboflow dashboard")
        print("   - Visit https://app.roboflow.com/2025-hackerthon")
        print("   - Go to Project > Version page > Click 'Use Model' button")
        print("   - Copy correct format from API code snippet")

    print("\n" + "="*80)


if __name__ == "__main__":
    run_comprehensive_test()
