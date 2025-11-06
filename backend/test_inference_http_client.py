"""
Roboflow InferenceHTTPClient로 Instant 모델 테스트
"""
import os
import sys
from dotenv import load_dotenv

# UTF-8 출력 강제
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
MODEL_ID = "2025-hackerthon/hackerthon2025-fnd8v-instant-2"
TEST_IMAGE = "../aws_bedrock/testcan.jpg"

print("="*80)
print("Roboflow InferenceHTTPClient Test")
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
print("InferenceHTTPClient 사용")
print("="*80)

try:
    from inference_sdk import InferenceHTTPClient

    print("\n[1] 클라이언트 초기화 중...")
    client = InferenceHTTPClient(
        api_url="https://detect.roboflow.com",
        api_key=ROBOFLOW_API_KEY
    )
    print("   [OK] 클라이언트 초기화 성공!")

    print("\n[2] 추론 실행 중...")
    result = client.infer(
        TEST_IMAGE,
        model_id=MODEL_ID
    )
    print("   [OK] 추론 성공!")

    print("\n[3] 결과 분석...")
    print(f"   Result type: {type(result)}")
    print(f"   Result keys: {result.keys() if isinstance(result, dict) else 'N/A'}")

    predictions = result.get('predictions', [])
    print(f"   Number of predictions: {len(predictions)}")

    if predictions:
        print(f"\n   감지된 객체:")
        for i, pred in enumerate(predictions[:5], 1):
            class_name = pred.get('class', 'unknown')
            confidence = pred.get('confidence', 0)
            x = pred.get('x', 0)
            y = pred.get('y', 0)
            width = pred.get('width', 0)
            height = pred.get('height', 0)
            print(f"      [{i}] {class_name}: {confidence:.2%}")
            print(f"          위치: x={x:.1f}, y={y:.1f}, w={width:.1f}, h={height:.1f}")

    print("\n" + "="*80)
    print("SUCCESS! InferenceHTTPClient로 Instant 모델 사용 가능!")
    print("="*80)

except ImportError as e:
    print(f"\n[ERROR] inference_sdk 패키지 import 실패: {e}")
    print("\n해결 방법:")
    print("   py -3.12 -m pip install inference-sdk")
    sys.exit(1)

except Exception as e:
    print(f"\n[ERROR] 추론 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*80)
