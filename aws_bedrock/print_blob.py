import os
import sys
import base64


def main():
    # 기본 파일 경로: 현재 파일과 같은 폴더의 testcan.jpg
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_path = os.path.join(script_dir, "testcan.jpg")

    # 인자 처리
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    flags = {a for a in sys.argv[1:] if a.startswith("-")}

    target_path = args[0] if args else default_path

    if not os.path.exists(target_path):
        print(f"❌ 파일을 찾을 수 없습니다: {target_path}")
        print("   사용법: python print_blob.py [이미지_경로] [--data-url]")
        sys.exit(1)

    # MIME 타입 추정 (간단 처리)
    lower = target_path.lower()
    if lower.endswith(".png"):
        mime = "image/png"
    elif lower.endswith(".jpg") or lower.endswith(".jpeg"):
        mime = "image/jpeg"
    elif lower.endswith(".gif"):
        mime = "image/gif"
    elif lower.endswith(".webp"):
        mime = "image/webp"
    else:
        mime = "application/octet-stream"

    # 파일 읽어서 Base64 인코딩 (프린트 친화적인 blob 표현)
    with open(target_path, "rb") as f:
        raw = f.read()

    b64 = base64.b64encode(raw).decode("utf-8")

    # --data-url 플래그가 있으면 Data URL로 출력
    if "--data-url" in flags:
        print(f"data:{mime};base64,{b64}")
    else:
        print(b64)


if __name__ == "__main__":
    main()


