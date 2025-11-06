"""
실제 /api/detect-qcode 엔드포인트 테스트
프론트엔드와 동일한 방식으로 API 호출
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
MODEL_ID = os.getenv("ROBOFLOW_MODEL_ID")
TEST_IMAGE = "../aws_bedrock/testcan.jpg"
API_URL = "http://localhost:8000/api/detect-qcode"

print("="*80)
print("실제 FastAPI 엔드포인트 테스트")
print("="*80)
print(f"\nConfiguration:")
print(f"   API URL: {API_URL}")
print(f"   Model ID (from .env): {MODEL_ID}")
print(f"   API Key: {ROBOFLOW_API_KEY[:10]}...{ROBOFLOW_API_KEY[-4:]}")
print(f"   Test Image: {TEST_IMAGE}")

# 이미지 파일 확인
if not os.path.exists(TEST_IMAGE):
    print(f"\n[ERROR] Test image not found: {TEST_IMAGE}")
    sys.exit(1)

print("\n" + "="*80)
print("FastAPI /api/detect-qcode 호출")
print("="*80)

try:
    print(f"\n[1] 이미지 로드 중...")
    with open(TEST_IMAGE, "rb") as image_file:
        files = {"file": ("frame.jpg", image_file, "image/jpeg")}

        print(f"[2] API 호출 중...")
        print(f"    URL: {API_URL}")

        response = requests.post(
            API_URL,
            files=files,
            timeout=30
        )

    print(f"\n[3] 응답 수신")
    print(f"    Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"\n[4] 응답 데이터:")
        print(f"    Success: {data.get('success')}")
        print(f"    Message: {data.get('message')}")

        if data.get('error'):
            print(f"    Error: {data.get('error')}")

        detected_products = data.get('detected_products', [])
        print(f"    Detected Products: {len(detected_products)}")

        if detected_products:
            print(f"\n    감지된 제품:")
            for i, product in enumerate(detected_products, 1):
                print(f"      [{i}] Q-CODE: {product.get('qcode')}")
                print(f"          Count: {product.get('detected_count')}")
                print(f"          Confidence: {product.get('confidence', 0):.2%}")

        if data.get('success'):
            print("\n" + "="*80)
            print("SUCCESS! API가 정상 작동합니다!")
            print("="*80)
        else:
            print("\n" + "="*80)
            print("API 호출은 성공했지만 제품 감지 실패")
            print("="*80)
            print("\n가능한 원인:")
            print("   1. Roboflow 모델 ID가 잘못되었거나")
            print("   2. 모델이 아직 완전히 배포되지 않았거나")
            print("   3. 테스트 이미지에 학습된 객체가 없음")

    else:
        print(f"\n[FAIL] Status Code: {response.status_code}")
        print(f"    Response: {response.text}")

except Exception as e:
    print(f"\n[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
