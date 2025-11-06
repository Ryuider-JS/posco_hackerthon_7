"""
샘플 앱에서 발견한 API Key로 테스트
"""
import os
import sys
import requests

# UTF-8 출력 강제
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# 샘플 앱의 설정
API_KEY_FROM_SAMPLE = "rf_XnkmP66mbATsu6CtP7OuJhIJ3ut1"
MODEL_ID = "hackerthon2025-fnd8v/2"
TEST_IMAGE = "../aws_bedrock/testcan.jpg"

print("="*80)
print("샘플 앱 API Key로 테스트")
print("="*80)
print(f"\nConfiguration:")
print(f"   Model ID: {MODEL_ID}")
print(f"   Sample App API Key: {API_KEY_FROM_SAMPLE[:10]}...{API_KEY_FROM_SAMPLE[-4:]}")
print(f"   Test Image: {TEST_IMAGE}")

# 이미지 파일 확인
if not os.path.exists(TEST_IMAGE):
    print(f"\n[ERROR] Test image not found: {TEST_IMAGE}")
    sys.exit(1)

print("\n" + "="*80)
print("REST API 테스트")
print("="*80)

try:
    url = f"https://detect.roboflow.com/{MODEL_ID}"

    print(f"\n[1] API 호출 중...")
    print(f"   URL: {url}")
    print(f"   API Key: {API_KEY_FROM_SAMPLE[:15]}...{API_KEY_FROM_SAMPLE[-4:]}")

    with open(TEST_IMAGE, "rb") as image_file:
        response = requests.post(
            url,
            params={"api_key": API_KEY_FROM_SAMPLE},
            files={"file": image_file},
            timeout=15
        )

    print(f"\n[2] 응답 수신")
    print(f"   Status Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        predictions = result.get('predictions', [])

        print(f"\n[SUCCESS!] {len(predictions)} objects detected!")
        print(f"\n[3] 결과 분석...")
        print(f"   Response keys: {result.keys()}")

        if predictions:
            print(f"\n   감지된 객체:")
            for i, pred in enumerate(predictions, 1):
                class_name = pred.get('class', 'unknown')
                confidence = pred.get('confidence', 0)
                print(f"      [{i}] {class_name}: {confidence:.2%}")

        print("\n" + "="*80)
        print("SUCCESS! 샘플 앱 API Key가 작동합니다!")
        print("="*80)
        print(f"\n.env 파일을 다음과 같이 업데이트하세요:")
        print(f"   ROBOFLOW_API_KEY={API_KEY_FROM_SAMPLE}")

    else:
        print(f"\n[FAIL] Status Code: {response.status_code}")
        print(f"   Response: {response.text}")

except Exception as e:
    print(f"\n[ERROR] {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
