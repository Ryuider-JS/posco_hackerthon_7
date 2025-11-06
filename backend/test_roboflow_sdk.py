"""
Roboflow Python SDK Test Script
공식 SDK를 사용한 간단한 테스트
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
TEST_IMAGE = "../aws_bedrock/testcan.jpg"

print("="*80)
print("Roboflow Python SDK Test")
print("="*80)

# SDK 설치 확인
try:
    from roboflow import Roboflow
    print("[OK] Roboflow SDK installed")
except ImportError:
    print("[ERROR] Roboflow SDK not installed")
    print("\nInstall with: pip install roboflow")
    sys.exit(1)

# 테스트 이미지 확인
if not os.path.exists(TEST_IMAGE):
    print(f"[ERROR] Test image not found: {TEST_IMAGE}")
    sys.exit(1)

print(f"\nConfiguration:")
print(f"   API Key: {ROBOFLOW_API_KEY[:10]}...{ROBOFLOW_API_KEY[-4:]}")
print(f"   Test Image: {TEST_IMAGE}")

print("\n" + "="*80)
print("Testing Different Workspace/Project Combinations")
print("="*80)

# 테스트할 워크스페이스/프로젝트 조합
test_configs = [
    # 참고 문서 예제 기반
    {
        "workspace": "2025-hackerthon",
        "project": "hackerthon2025",
        "version": 2
    },
    {
        "workspace": "2025-hackerthon",
        "project": "hackerthon2025-fnd8v",
        "version": 2
    },
    {
        "workspace": "2025-hackerthon",
        "project": "hackerthon2025-fnd8v-instant",
        "version": 2
    },
    # 버전을 1로 시도
    {
        "workspace": "2025-hackerthon",
        "project": "hackerthon2025",
        "version": 1
    },
    {
        "workspace": "2025-hackerthon",
        "project": "hackerthon2025-fnd8v",
        "version": 1
    },
]

successful_config = None

for i, config in enumerate(test_configs, 1):
    print(f"\n[Test {i}/{len(test_configs)}]")
    print(f"   Workspace: {config['workspace']}")
    print(f"   Project: {config['project']}")
    print(f"   Version: {config['version']}")

    try:
        # Roboflow 초기화
        rf = Roboflow(api_key=ROBOFLOW_API_KEY)

        # 워크스페이스 접근
        workspace = rf.workspace(config['workspace'])
        print(f"   [OK] Workspace accessed")

        # 프로젝트 접근
        project = workspace.project(config['project'])
        print(f"   [OK] Project accessed")

        # 버전 및 모델 접근
        version = project.version(config['version'])
        model = version.model
        print(f"   [OK] Model loaded")

        # 추론 실행
        prediction = model.predict(TEST_IMAGE, confidence=40, overlap=30)
        result = prediction.json()

        predictions = result.get('predictions', [])
        print(f"   [SUCCESS] {len(predictions)} objects detected!")

        if predictions:
            for pred in predictions[:3]:
                class_name = pred.get('class', 'unknown')
                confidence = pred.get('confidence', 0)
                print(f"      * {class_name}: {confidence:.2%}")

        successful_config = config
        break  # 성공하면 중단

    except Exception as e:
        error_msg = str(e)[:200]
        print(f"   [FAIL] {error_msg}")

print("\n" + "="*80)
print("FINAL RESULT")
print("="*80)

if successful_config:
    print(f"\n[SUCCESS] Working configuration found!\n")
    print(f"Workspace: {successful_config['workspace']}")
    print(f"Project: {successful_config['project']}")
    print(f"Version: {successful_config['version']}")

    print("\n" + "="*80)
    print("CODE TO USE IN YOUR APPLICATION")
    print("="*80)

    print(f"""
from roboflow import Roboflow

rf = Roboflow(api_key="{ROBOFLOW_API_KEY[:10]}...")
project = rf.workspace("{successful_config['workspace']}").project("{successful_config['project']}")
model = project.version({successful_config['version']}).model

# Run inference
prediction = model.predict("image.jpg", confidence=40, overlap=30)
result = prediction.json()
print(result['predictions'])
""")

else:
    print("\n[FAIL] No working configuration found")
    print("\nPossible solutions:")
    print("   1. Check workspace name on Roboflow dashboard")
    print("   2. Check exact project name")
    print("   3. Verify model has been trained")
    print("   4. Try listing all projects:")
    print("\nTry this code to list your projects:")
    print(f"""
from roboflow import Roboflow
rf = Roboflow(api_key="{ROBOFLOW_API_KEY[:10]}...")
workspace = rf.workspace("2025-hackerthon")
print(workspace.projects())
""")

print("\n" + "="*80)
