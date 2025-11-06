"""
Roboflow Inference Package Test
inference 패키지로 Instant 모델 테스트
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
# Instant 모델의 전체 ID 사용
MODEL_ID = "2025-hackerthon/hackerthon2025-fnd8v-instant-2"
TEST_IMAGE = "../aws_bedrock/testcan.jpg"

print("="*80)
print("Roboflow Inference Package Test")
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
print("Method 1: get_model() 함수 사용")
print("="*80)

try:
    from inference import get_model
    import cv2

    print("\n[1] 모델 로드 중...")
    model = get_model(
        model_id=MODEL_ID,
        api_key=ROBOFLOW_API_KEY
    )
    print("   [OK] 모델 로드 성공!")

    print("\n[2] 이미지 로드 중...")
    image = cv2.imread(TEST_IMAGE)
    if image is None:
        print(f"   [ERROR] Failed to load image: {TEST_IMAGE}")
        sys.exit(1)
    print(f"   [OK] 이미지 로드 성공! Shape: {image.shape}")

    print("\n[3] 추론 실행 중...")
    results = model.infer(image)
    print("   [OK] 추론 성공!")

    print("\n[4] 결과 분석...")
    print(f"   Results type: {type(results)}")
    print(f"   Results: {results}")

    # predictions 추출
    if hasattr(results, 'predictions'):
        predictions = results.predictions
    elif isinstance(results, dict) and 'predictions' in results:
        predictions = results['predictions']
    elif isinstance(results, list):
        predictions = results[0].predictions if hasattr(results[0], 'predictions') else results
    else:
        predictions = results

    print(f"\n   Predictions type: {type(predictions)}")
    print(f"   Number of predictions: {len(predictions) if hasattr(predictions, '__len__') else 'N/A'}")

    if predictions:
        print(f"\n   감지된 객체:")
        for i, pred in enumerate(predictions[:5], 1):
            if hasattr(pred, 'class_name'):
                class_name = pred.class_name
                confidence = pred.confidence
            elif isinstance(pred, dict):
                class_name = pred.get('class', 'unknown')
                confidence = pred.get('confidence', 0)
            else:
                class_name = str(pred)
                confidence = 'N/A'

            print(f"      [{i}] {class_name}: {confidence if isinstance(confidence, str) else f'{confidence:.2%}'}")

    print("\n" + "="*80)
    print("SUCCESS! inference 패키지로 Instant 모델 사용 가능!")
    print("="*80)

except ImportError as e:
    print(f"\n[ERROR] inference 패키지 import 실패: {e}")
    print("\n해결 방법:")
    print("   py -3.12 -m pip install inference")
    sys.exit(1)

except Exception as e:
    print(f"\n[ERROR] 추론 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*80)
print("Method 2: InferenceHTTPClient 사용")
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
    predictions = result.get('predictions', [])
    print(f"   Number of predictions: {len(predictions)}")

    if predictions:
        print(f"\n   감지된 객체:")
        for i, pred in enumerate(predictions[:5], 1):
            class_name = pred.get('class', 'unknown')
            confidence = pred.get('confidence', 0)
            print(f"      [{i}] {class_name}: {confidence:.2%}")

    print("\n" + "="*80)
    print("SUCCESS! InferenceHTTPClient로도 사용 가능!")
    print("="*80)

except ImportError:
    print("\n[INFO] inference_sdk 패키지 없음 (선택사항)")
    print("   inference 패키지의 get_model() 사용을 권장합니다.")

except Exception as e:
    print(f"\n[INFO] InferenceHTTPClient 테스트 실패 (정상)")
    print(f"   이유: {e}")
    print("   => get_model() 방식을 사용하세요!")

print("\n" + "="*80)
