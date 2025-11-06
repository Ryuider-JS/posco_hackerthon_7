"""
S3 이미지 URL을 사용하여 Knowledge Base에서 가장 유사한 제품 찾기
S3 URL을 텍스트로 전달하여 Knowledge Base에서 가장 유사한 제품의 파일명을 반환합니다.
"""
import boto3
import json
import os
from config import AWSConfig

# 환경변수에서 설정 가져오기
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Bedrock Agent Runtime 클라이언트 생성
region = os.getenv("AWS_REGION", "ap-northeast-2")  # 서울 리전
bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name=region)

# Knowledge Base ID (환경변수 또는 config에서 가져오기)
knowledge_base_id = os.getenv("KNOWLEDGE_BASE_ID", AWSConfig.knowledge_base_id)

# S3 이미지 경로
s3_uri = "s3://posco-bedrock-vector-s3-12jo/wx_hackerton/product_new/testcan.jpg"

print(f"📸 S3 이미지 경로: {s3_uri}")
print()

# Knowledge Base에서 유사한 이미지 검색
if not knowledge_base_id:
    print("⚠️  Knowledge Base ID가 설정되지 않았습니다.")
    print("   환경변수 KNOWLEDGE_BASE_ID 또는 config.py의 knowledge_base_id를 설정하세요.")
    exit(1)

print("🔎 Knowledge Base에서 유사한 제품 검색 중...")
print(f"   Knowledge Base ID: {knowledge_base_id}")
print()

try:
    # Knowledge Base 검색 쿼리 생성
    # S3 URL을 텍스트로 포함하여 유사한 제품 검색
    search_query = f"{s3_uri}"
    
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
        filename = None
        
        # 메타데이터에서 파일명 찾기
        metadata = best_match.get('metadata', {})
        location = best_match.get('location', {})
        
        # S3 URI에서 파일명 추출
        if 's3Location' in location:
            s3_uri_result = location['s3Location'].get('uri', '')
            if s3_uri_result:
                # s3://bucket/key 형식에서 파일명 추출
                if s3_uri_result.startswith('s3://'):
                    filename = s3_uri_result.split('/')[-1]
                else:
                    filename = s3_uri_result.split('/')[-1]
        
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
                r's3://[^/]+/[^/]+/([^\s]+\.(jpg|jpeg|png|gif|webp))',
            ]
            for pattern in patterns:
                match = re.search(pattern, best_text, re.IGNORECASE)
                if match:
                    filename = match.group(1) if match.groups() else match.group(0)
                    break
        
        print(f"🎯 가장 유사한 제품:")
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
                
                # 각 결과에서도 파일명 추출 시도
                result_filename = None
                result_location = result.get('location', {})
                if 's3Location' in result_location:
                    result_s3_uri = result_location['s3Location'].get('uri', '')
                    if result_s3_uri:
                        result_filename = result_s3_uri.split('/')[-1]
                
                filename_display = result_filename if result_filename else "(추출 불가)"
                print(f"   {i}. 점수: {score:.4f}, 파일명: {filename_display}, 내용: {text[:100]}...")
        
        print("-" * 50)
        
        # 파일명 반환
        if filename:
            print(f"\n✅ 가장 유사한 제품 파일명: {filename}")
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
            r's3://[^/]+/[^/]+/([^\s]+\.(jpg|jpeg|png|gif|webp))',
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
