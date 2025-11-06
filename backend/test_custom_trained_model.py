"""
커스텀 트레이닝 모델 테스트
hackerthon2025-fnd8v/2
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
MODEL_ID = "hackerthon2025-fnd8v/2"  # 커스텀 트레이닝 완료 모델
TEST_IMAGE = "../aws_bedrock/testcan.jpg"

print("="*80)
print("커스텀 트레이닝 모델 테스트")
print("="*80)
print(f"\nConfiguration:")
print(f"   Model ID: {MODEL_ID}")
print(f"   API Key: {ROBOFLOW_API_KEY[:10]}...{ROBOFLOW_API_KEY[-4:]}")
print(f"   Test Image: {TEST_IMAGE}")

# 이미지 파일 확인
if not os.path.exists(TEST_IMAGE):
    print(f"\n[ERROR] Test image not found: {TEST_IMAGE}")
    sys.exit(1)

print("\n" + "="*80)
print("REST API 테스트 (multipart/form-data)")
print("="*80)

try:
    url = f"https://detect.roboflow.com/{MODEL_ID}"

    print(f"\n[1] API 호출 중...")
    print(f"   URL: {url}")

    with open(TEST_IMAGE, "rb") as image_file:
        response = requests.post(
            url,
            params={"api_key": ROBOFLOW_API_KEY},
            files={"file": image_file},
            timeout=15
        )

    print(f"   Status Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        predictions = result.get('predictions', [])

        print(f"\n[SUCCESS!] {len(predictions)} objects detected!")
        print("\n[2] 결과 분석...")
        print(f"   Response keys: {result.keys()}")
        print(f"   Number of predictions: {len(predictions)}")

        if predictions:
            print(f"\n   감지된 객체:")
            for i, pred in enumerate(predictions, 1):
                class_name = pred.get('class', 'unknown')
                confidence = pred.get('confidence', 0)
                x = pred.get('x', 0)
                y = pred.get('y', 0)
                width = pred.get('width', 0)
                height = pred.get('height', 0)

                print(f"      [{i}] {class_name}: {confidence:.2%}")
                print(f"          위치: x={x:.1f}, y={y:.1f}, w={width:.1f}, h={height:.1f}")

        print("\n" + "="*80)
        print("SUCCESS! 커스텀 모델이 정상 작동합니다!")
        print("="*80)
        print(f"\n.env 파일 업데이트:")
        print(f"   ROBOFLOW_MODEL_ID={MODEL_ID}")
        print(f"\n현재 roboflow_service.py의 코드를 그대로 사용할 수 있습니다!")

    else:
        print(f"\n[FAIL] Status Code: {response.status_code}")
        print(f"   Response: {response.text[:500]}")

except Exception as e:
    print(f"\n[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
