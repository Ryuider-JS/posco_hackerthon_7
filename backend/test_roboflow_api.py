"""
Roboflow CLIP API 테스트 스크립트
"""
import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY")
CLIP_EMBED_URL = "https://infer.roboflow.com/clip/embed_image"

def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def test_clip_api():
    # 테스트 이미지 경로
    test_image = "../product_list_picture/Q1208172/Q1208172_1.png"

    print(f"[*] Testing Roboflow CLIP API")
    print(f"    API Key: {ROBOFLOW_API_KEY[:10] if ROBOFLOW_API_KEY else 'NOT SET'}...")
    print(f"    Test Image: {test_image}")

    # 이미지 인코딩
    image_base64 = encode_image_to_base64(test_image)
    print(f"    Base64 length: {len(image_base64)} chars")

    # 페이로드 구성
    payload = {
        "image": {
            "type": "base64",
            "value": image_base64
        }
    }

    # API 호출
    print(f"\n[*] Sending request to: {CLIP_EMBED_URL}")
    response = requests.post(
        CLIP_EMBED_URL,
        params={"api_key": ROBOFLOW_API_KEY},
        json=payload
    )

    print(f"    Status Code: {response.status_code}")
    print(f"    Response Headers: {dict(response.headers)}")
    print(f"    Response Body: {response.text[:500]}")

    if response.status_code == 200:
        result = response.json()
        if "embeddings" in result:
            print(f"\n[OK] Embeddings received!")
            print(f"    Embedding shape: {len(result['embeddings'])}")
            print(f"    First embedding length: {len(result['embeddings'][0])}")
        else:
            print(f"\n[ERROR] No embeddings in response!")
    else:
        print(f"\n[ERROR] API request failed!")

if __name__ == "__main__":
    test_clip_api()
