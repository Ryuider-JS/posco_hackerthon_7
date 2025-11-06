# AWS Bedrock 이미지 처리 및 Knowledge Base 검색

## 설치

```bash
pip install -r requirements.txt
```

## AWS 환경변수 설정

PowerShell에서 다음 명령어 실행:

```powershell
$env:S3_BUCKET_NAME="posco-bedrock-vector-s3-12jo"
$env:S3_FOLDER="wx_hackerton/product_pic"
$env:AWS_ACCESS_KEY_ID="your-access-key-id"
$env:AWS_SECRET_ACCESS_KEY="your-secret-access-key"
$env:AWS_REGION="ap-northeast-2"
$env:KNOWLEDGE_BASE_ID="your-knowledge-base-id"
```

또는 `.env` 파일 생성:

```
S3_BUCKET_NAME=posco-bedrock-vector-s3-12jo
S3_FOLDER=wx_hackerton/product_pic
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_REGION=ap-northeast-2
KNOWLEDGE_BASE_ID=your-knowledge-base-id
```

## 사용 방법

### 1. S3 이미지 업로드

`test.png` 파일을 프로젝트 폴더에 준비하고 실행:

```bash
python upload_image.py
```

### 2. Knowledge Base를 사용한 이미지 유사도 검색

`multi_modal.py`를 실행하여 입력 이미지를 분석하고 Knowledge Base에서 가장 유사한 이미지를 찾습니다:

```bash
python multi_modal.py
```

**동작 방식:**
1. 입력 이미지를 Claude Vision 모델로 분석하여 텍스트 설명 생성
2. 생성된 설명을 기반으로 Knowledge Base에서 유사한 이미지 검색
3. 가장 유사한 이미지의 파일명 반환

**설정:**
- Knowledge Base ID는 `config.py`의 `knowledge_base_id` 또는 환경변수 `KNOWLEDGE_BASE_ID`로 설정
- 이미지 파일명: `can.jpg`, `testcan.jpg`, `test.jpg` 중 하나를 사용

### 3. Bedrock Agent와 대화

```bash
python call_bedrock.py
```

## 파일 구조

- `s3_uploader.py` - S3 업로드 클래스
- `upload_image.py` - test.png 업로드 스크립트
- `multi_modal.py` - Knowledge Base를 사용한 이미지 유사도 검색
- `call_bedrock.py` - Bedrock Agent와 대화
- `config.py` - AWS 설정 (Agent ID, Knowledge Base ID 등)