"""
Knowledge Base를 연결하여 이미지 유사도 검색
입력 이미지를 분석하고 Knowledge Base에서 가장 유사한 이미지를 찾아 파일명을 반환합니다.
"""
import boto3
import json
import base64
import os
from config import AWSConfig

# 환경변수에서 설정 가져오기
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Bedrock Runtime 및 Agent Runtime 클라이언트 생성
region = os.getenv("AWS_REGION", "ap-northeast-2")  # 서울 리전
bedrock_runtime = boto3.client("bedrock-runtime", region_name=region)
bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name=region)

# Knowledge Base ID (환경변수 또는 config에서 가져오기)
knowledge_base_id = os.getenv("KNOWLEDGE_BASE_ID", AWSConfig.knowledge_base_id)

# 로컬 이미지 파일 경로
image_path = "can.jpg"

# 이미지 파일 찾기 (대소문자 구분 없이)
if not os.path.exists(image_path):
    found = False
    for filename in ["testcan.jpg", "testcan.JPG", "can.jpg", "can.JPG", "test.jpg", "test.JPG"]:
        if os.path.exists(filename):
            image_path = filename
            found = True
            break
    if not found:
        print(f"❌ 이미지 파일을 찾을 수 없습니다.")
        print(f"   다음 파일명을 확인하세요: testcan.jpg, can.jpg, test.jpg")
        exit(1)

print(f"📸 이미지 로드: {image_path}")

# 이미지를 base64로 인코딩
with open(image_path, "rb") as image_file:
    image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    
    # 이미지 타입 감지
    if image_path.lower().endswith('.png'):
        image_type = "image/png"
    elif image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
        image_type = "image/jpeg"
    else:
        image_type = "image/jpeg"

print(f"   타입: {image_type}")
print(f"   크기: {len(image_base64)} bytes (base64)")
print()

# 1단계: Claude를 사용하여 이미지 분석 (텍스트 설명 생성)
print("🔍 이미지 분석 중...")
try:
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": image_type,
                            "data": image_base64
                        }
                    },
                    {
                        "type": "text",
                        "text": "이 이미지를 자세히 분석하고, 제품의 특징, 색상, 형태, 크기, 브랜드 등을 포함한 상세한 설명을 텍스트로 작성해주세요. 이 설명은 유사한 제품을 검색하는데 사용됩니다."
                    }
                ]
            }
        ]
    }
    
    # Claude 모델 호출 시도
    model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    try:
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=json.dumps(payload),
        )
        result = json.loads(response["body"].read())
        image_description = result["content"][0]["text"]
        print("✅ 이미지 분석 완료")
        print(f"   설명: {image_description[:100]}...")
        print()
    except Exception as e:
        # 다른 모델 시도 (Claude 3 Haiku)
        if "on-demand throughput" in str(e) or "inference profile" in str(e).lower():
            print("⚠️  Inference profile 필요. Claude 3 Haiku 시도 중...")
            try:
                model_id = "anthropic.claude-3-haiku-20240307-v1:0"
                response = bedrock_runtime.invoke_model(
                    modelId=model_id,
                    body=json.dumps(payload),
                )
                result = json.loads(response["body"].read())
                image_description = result["content"][0]["text"]
                print("✅ 이미지 분석 완료 (Claude 3 Haiku)")
                print(f"   설명: {image_description[:100]}...")
                print()
            except Exception as e2:
                print(f"❌ 모델 호출 실패: {e2}")
                # 간단한 설명으로 대체
                image_description = "제품 이미지"
                print(f"⚠️  기본 설명 사용: {image_description}")
        else:
            raise e

except Exception as e:
    print(f"❌ 이미지 분석 중 오류: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# 2단계: Knowledge Base에서 유사한 이미지 검색
if not knowledge_base_id:
    print("⚠️  Knowledge Base ID가 설정되지 않았습니다.")
    print("   환경변수 KNOWLEDGE_BASE_ID 또는 config.py의 knowledge_base_id를 설정하세요.")
    print()
    print("💡 이미지 설명:")
    print("-" * 50)
    print(image_description)
    print("-" * 50)
    exit(1)

print("🔎 Knowledge Base에서 유사한 이미지 검색 중...")
print(f"   Knowledge Base ID: {knowledge_base_id}")
print()

try:
    # Knowledge Base 검색 쿼리 생성
    # 이미지 설명을 기반으로 유사한 제품 검색
    search_query = f"다음 설명과 가장 유사한 제품 이미지를 찾아주세요. 파일명을 반환해주세요: {image_description}"
    
    # retrieve API 사용 (Knowledge Base에서 직접 검색)
    response = bedrock_agent_runtime.retrieve(
        knowledgeBaseId=knowledge_base_id,
        retrievalQuery={
            "text": search_query
        },
        retrievalConfiguration={
            "vectorSearchConfiguration": {
                "numberOfResults": 5  # 상위 5개 결과 반환
            }
        }
    )
    
    print("✅ 검색 완료")
    print()
    print("📋 검색 결과:")
    print("-" * 50)
    
    # 검색 결과 처리
    retrieval_results = response.get('retrievalResults', [])
    
    if not retrieval_results:
        print("⚠️  검색 결과가 없습니다.")
    else:
        # 가장 유사한 결과 (첫 번째 결과)
        best_match = retrieval_results[0]
        best_score = best_match.get('score', 0)
        best_content = best_match.get('content', {})
        best_text = best_content.get('text', '')
        
        # 파일명 추출 시도
        # 파일명은 일반적으로 메타데이터나 텍스트에 포함되어 있을 수 있습니다
        filename = None
        
        # 메타데이터에서 파일명 찾기
        metadata = best_match.get('metadata', {})
        location = best_match.get('location', {})
        
        # S3 URI에서 파일명 추출
        if 's3Location' in location:
            s3_uri = location['s3Location'].get('uri', '')
            if s3_uri:
                filename = s3_uri.split('/')[-1]  # 마지막 경로가 파일명
        
        # 메타데이터에서 파일명 찾기
        if not filename:
            filename = metadata.get('file_name') or metadata.get('filename') or metadata.get('name')
        
        # 텍스트에서 파일명 패턴 찾기
        if not filename and best_text:
            import re
            # 일반적인 이미지 파일 확장자 패턴
            patterns = [
                r'([^\s]+\.(jpg|jpeg|png|gif|webp))',
                r'파일명[:\s]+([^\s]+)',
                r'filename[:\s]+([^\s]+)',
            ]
            for pattern in patterns:
                match = re.search(pattern, best_text, re.IGNORECASE)
                if match:
                    filename = match.group(1) if match.groups() else match.group(0)
                    break
        
        print(f"🎯 가장 유사한 결과:")
        print(f"   유사도 점수: {best_score:.4f}")
        if filename:
            print(f"   파일명: {filename}")
        else:
            print(f"   파일명: (추출 불가)")
        print(f"   내용: {best_text[:200]}...")
        print()
        
        # 다른 결과들도 표시
        if len(retrieval_results) > 1:
            print("📊 다른 검색 결과:")
            for i, result in enumerate(retrieval_results[1:], 2):
                score = result.get('score', 0)
                content = result.get('content', {})
                text = content.get('text', '')
                print(f"   {i}. 점수: {score:.4f}, 내용: {text[:100]}...")
        
        print("-" * 50)
        
        # 파일명 반환
        if filename:
            print(f"\n✅ 가장 유사한 이미지 파일명: {filename}")
        else:
            print(f"\n⚠️  파일명을 자동으로 추출할 수 없습니다.")
            print(f"   검색 결과 텍스트를 확인하세요:")
            print(f"   {best_text}")

except bedrock_agent_runtime.exceptions.ValidationException as e:
    print(f"❌ 검증 오류: {e}")
    print("\n💡 해결 방법:")
    print("   1. Knowledge Base ID가 올바른지 확인")
    print("   2. Knowledge Base가 활성화되어 있는지 확인")
    print("   3. Knowledge Base 접근 권한 확인")
except bedrock_agent_runtime.exceptions.AccessDeniedException as e:
    print(f"❌ 접근 거부: {e}")
    print("\n💡 해결 방법:")
    print("   1. AWS 자격 증명 확인")
    print("   2. Knowledge Base 접근 권한 확인")
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()
    
    # retrieve API가 지원되지 않을 경우, retrieve_and_generate 시도
    print("\n🔄 retrieve_and_generate API 시도 중...")
    try:
        response = bedrock_agent_runtime.retrieve_and_generate(
            input={
                "text": search_query
            },
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": knowledge_base_id,
                    "modelArn": f"arn:aws:bedrock:{region}::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"
                }
            }
        )
        
        print("✅ retrieve_and_generate 성공")
        output = response.get('output', {})
        text = output.get('text', '')
        
        print("\n📋 결과:")
        print("-" * 50)
        print(text)
        print("-" * 50)
        
        # 파일명 추출
        import re
        patterns = [
            r'([^\s]+\.(jpg|jpeg|png|gif|webp))',
            r'파일명[:\s]+([^\s]+)',
            r'filename[:\s]+([^\s]+)',
        ]
        filename = None
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                filename = match.group(1) if match.groups() else match.group(0)
                break
        
        if filename:
            print(f"\n✅ 파일명: {filename}")
        else:
            print(f"\n⚠️  파일명을 자동으로 추출할 수 없습니다.")
        
    except Exception as e2:
        print(f"❌ retrieve_and_generate도 실패: {e2}")
