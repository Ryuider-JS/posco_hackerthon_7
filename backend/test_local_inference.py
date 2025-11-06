"""
로컬 Inference 서버를 사용한 Roboflow Instant 모델 테스트
inference 패키지는 로컬 추론을 지원합니다
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
# Instant 모델 ID 형식
MODEL_ID = "hackerthon2025-fnd8v-instant-2"  # workspace는 제외
WORKSPACE = "2025-hackerthon"
VERSION = "2"
TEST_IMAGE = "../aws_bedrock/testcan.jpg"

print("="*80)
print("로컬 Inference로 Roboflow Instant 모델 테스트")
print("="*80)
print(f"\nConfiguration:")
print(f"   Workspace: {WORKSPACE}")
print(f"   Model ID: {MODEL_ID}")
print(f"   Version: {VERSION}")
print(f"   API Key: {ROBOFLOW_API_KEY[:10]}...{ROBOFLOW_API_KEY[-4:]}")
print(f"   Test Image: {TEST_IMAGE}")

# 이미지 파일 확인
if not os.path.exists(TEST_IMAGE):
    print(f"\n[ERROR] Test image not found: {TEST_IMAGE}")
    sys.exit(1)

# 다양한 모델 ID 형식 테스트
model_id_formats = [
    f"{WORKSPACE}/{MODEL_ID}",  # 2025-hackerthon/hackerthon2025-fnd8v-instant-2
    f"{WORKSPACE}/{VERSION}",  # 2025-hackerthon/2
    MODEL_ID,  # hackerthon2025-fnd8v-instant-2
    f"{MODEL_ID}/{VERSION}",  # hackerthon2025-fnd8v-instant-2/2
]

print("\n" + "="*80)
print("다양한 모델 ID 형식 테스트")
print("="*80)

for i, model_id in enumerate(model_id_formats, 1):
    print(f"\n[Test {i}/{len(model_id_formats)}] 모델 ID: {model_id}")
    print("-" * 80)

    try:
        from inference_sdk import InferenceHTTPClient

        # 로컬 Inference 서버 사용 (기본 포트: 9001)
        # 또는 Roboflow 호스팅 서버 사용
        for api_url in ["http://localhost:9001", "https://detect.roboflow.com"]:
            print(f"\n   API URL: {api_url}")

            try:
                client = InferenceHTTPClient(
                    api_url=api_url,
                    api_key=ROBOFLOW_API_KEY
                )

                result = client.infer(
                    TEST_IMAGE,
                    model_id=model_id
                )

                # 성공!
                predictions = result.get('predictions', [])
                print(f"   [SUCCESS!] {len(predictions)} objects detected!")

                if predictions:
                    print(f"\n   감지된 객체:")
                    for j, pred in enumerate(predictions[:3], 1):
                        class_name = pred.get('class', 'unknown')
                        confidence = pred.get('confidence', 0)
                        print(f"      [{j}] {class_name}: {confidence:.2%}")

                print("\n" + "="*80)
                print("SUCCESS! 작동하는 설정을 찾았습니다!")
                print("="*80)
                print(f"\n최종 설정:")
                print(f"   Model ID: {model_id}")
                print(f"   API URL: {api_url}")
                print(f"\n.env 파일 업데이트:")
                print(f"   ROBOFLOW_MODEL_ID={model_id}")
                print(f"\nroboflow_service.py 업데이트:")
                print(f"   INFERENCE_URL = \"{api_url}\"")
                sys.exit(0)

            except Exception as e:
                error_msg = str(e)
                if "Connection" in error_msg or "localhost" in api_url:
                    print(f"   [SKIP] 로컬 서버 없음: {error_msg[:100]}")
                else:
                    print(f"   [FAIL] {error_msg[:200]}")

    except Exception as e:
        print(f"   [ERROR] {str(e)[:200]}")

print("\n" + "="*80)
print("모든 설정 실패")
print("="*80)
print("\n가능한 원인:")
print("   1. Roboflow Instant 모델이 완전히 학습되지 않았거나")
print("   2. 호스팅 API가 Instant 모델을 지원하지 않거나")
print("   3. 로컬 Inference 서버가 필요합니다")
print("\n해결 방법:")
print("   [방법 1] 로컬 Inference 서버 실행:")
print("      docker run -p 9001:9001 roboflow/roboflow-inference-server-gpu")
print("   [방법 2] Custom Training 사용 (1-3시간 소요):")
print("      Roboflow Dashboard → Train Model → Custom Training → RF-DETR")
print("\n" + "="*80)
