import os
import google.generativeai as genai
from typing import Dict, List
from dotenv import load_dotenv
import json

load_dotenv()

def get_gemini_model():
    """Initialize Gemini API"""
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    return genai.GenerativeModel('gemini-1.5-flash')

def analyze_product_image_gemini(image_path: str) -> Dict:
    """
    Analyze product image using Gemini Vision API
    Returns product characteristics and extracted information
    """
    try:
        model = get_gemini_model()

        # Read image file
        with open(image_path, 'rb') as f:
            image_data = f.read()

        # Create image part
        image_part = {
            "mime_type": "image/jpeg",
            "data": image_data
        }

        prompt = """이 제품 이미지를 분석하여 다음 정보를 추출해주세요:

1. 제품명 (가능한 구체적으로)
2. 카테고리 (예: 기계부품, 체결부품, 전자부품 등)
3. 재질 (예: 스테인리스, 철, 플라스틱 등)
4. 크기/치수 (추정 가능한 경우)
5. 주요 특징 및 용도
6. 검색 키워드 (유사 제품 검색에 사용할 수 있는 키워드들)

JSON 형식으로만 응답해주세요 (다른 텍스트 없이):
{
    "name": "제품명",
    "category": "카테고리",
    "material": "재질",
    "dimensions": "크기/치수",
    "description": "상세 설명",
    "keywords": ["키워드1", "키워드2", ...]
}"""

        response = model.generate_content([prompt, image_part])
        result_text = response.text.strip()

        # Remove markdown code blocks if present
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        result_text = result_text.strip()

        # Try to parse JSON response
        try:
            parsed_result = json.loads(result_text)
            return {
                "success": True,
                "analysis": parsed_result,
                "raw_text": result_text
            }
        except json.JSONDecodeError:
            return {
                "success": True,
                "analysis": None,
                "raw_text": result_text
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "raw_text": f"이미지 분석 중 오류 발생: {str(e)}"
        }

def compare_images_similarity_gemini(image1_path: str, image2_path: str) -> Dict:
    """
    Compare two product images and return similarity score using Gemini
    """
    try:
        model = get_gemini_model()

        # Read both images
        with open(image1_path, 'rb') as f:
            image1_data = f.read()
        with open(image2_path, 'rb') as f:
            image2_data = f.read()

        image1_part = {"mime_type": "image/jpeg", "data": image1_data}
        image2_part = {"mime_type": "image/jpeg", "data": image2_data}

        prompt = """두 제품 이미지를 비교하여 유사도를 분석해주세요.

다음 기준으로 평가하고 0-100 점수로 응답해주세요:
1. 외형 유사도
2. 색상 유사도
3. 크기/형태 유사도
4. 재질 유사도
5. 전체적인 제품 특성 유사도

JSON 형식으로만 응답해주세요:
{
    "similarity_score": 85,
    "visual_similarity": 90,
    "color_similarity": 80,
    "shape_similarity": 85,
    "material_similarity": 85,
    "explanation": "두 제품이 매우 유사합니다. 외형과 색상이 거의 동일하며...",
    "differences": "주요 차이점은 크기가 약간 다를 수 있습니다..."
}"""

        response = model.generate_content([prompt, image1_part, image2_part])
        result_text = response.text.strip()

        # Clean up markdown
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        result_text = result_text.strip()

        try:
            parsed_result = json.loads(result_text)
            return {
                "success": True,
                "similarity": parsed_result.get("similarity_score", 0),
                "details": parsed_result,
                "raw_text": result_text
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "similarity": 0,
                "error": "JSON 파싱 실패",
                "raw_text": result_text
            }

    except Exception as e:
        return {
            "success": False,
            "similarity": 0,
            "error": str(e),
            "raw_text": f"이미지 비교 중 오류 발생: {str(e)}"
        }

def count_products_in_frame(image_path: str, registered_products: List[Dict]) -> Dict:
    """
    웹캠 프레임 내 각 제품의 개수를 세는 함수

    Args:
        image_path: 웹캠 프레임 이미지 경로
        registered_products: 등록된 제품 정보 리스트

    Returns:
        {
            "success": True,
            "detected_products": [
                {"qcode": "Q-2411-1234", "name": "육각볼트", "count": 5, "confidence": 0.9},
                {"qcode": "Q-2411-5678", "name": "너트", "count": 3, "confidence": 0.85}
            ]
        }
    """
    try:
        model = get_gemini_model()

        # Read webcam frame
        with open(image_path, 'rb') as f:
            image_data = f.read()

        image_part = {"mime_type": "image/jpeg", "data": image_data}

        # 등록된 제품 정보를 프롬프트에 포함
        product_list = "\n".join([
            f"- {p.get('name', 'Unknown')} (Q-CODE: {p.get('qcode', 'N/A')})"
            for p in registered_products
        ])

        prompt = f"""이 웹캠 이미지에서 다음 등록된 제품들이 각각 몇 개씩 보이는지 세어주세요.

등록된 제품 목록:
{product_list}

**중요**: 이미지에 실제로 보이는 제품만 카운팅하세요. 보이지 않는 제품은 포함하지 마세요.

각 제품의 개수와 신뢰도(0.0-1.0)를 JSON 형식으로만 응답해주세요:
{{
    "detected_products": [
        {{
            "qcode": "Q-CODE",
            "name": "제품명",
            "count": 개수,
            "confidence": 0.9
        }}
    ],
    "total_count": 전체개수,
    "notes": "감지 결과에 대한 간단한 설명"
}}

제품이 하나도 보이지 않으면 detected_products를 빈 배열[]로 반환하세요."""

        response = model.generate_content([prompt, image_part])
        result_text = response.text.strip()

        # Clean up markdown
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        result_text = result_text.strip()

        try:
            parsed_result = json.loads(result_text)
            return {
                "success": True,
                "detected_products": parsed_result.get("detected_products", []),
                "total_count": parsed_result.get("total_count", 0),
                "notes": parsed_result.get("notes", ""),
                "raw_text": result_text
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "detected_products": [],
                "error": "JSON 파싱 실패",
                "raw_text": result_text
            }

    except Exception as e:
        return {
            "success": False,
            "detected_products": [],
            "error": str(e),
            "raw_text": f"제품 카운팅 중 오류 발생: {str(e)}"
        }

def calculate_similarity_with_gemini(analysis: Dict, existing_products: List[Dict], uploaded_image_path: str) -> List[Dict]:
    """
    Compare analyzed product with existing products using Gemini for visual similarity
    Combines text-based similarity with visual similarity
    """
    from app.services.ai_service import calculate_similarity

    similar_products = []

    for product in existing_products:
        # Text-based similarity (from OpenAI analysis)
        text_similarity = calculate_similarity(analysis, product)

        # Visual similarity (from Gemini if product has image)
        visual_similarity = 0
        if product.get("image_path") and os.path.exists(product["image_path"]):
            try:
                gemini_result = compare_images_similarity_gemini(
                    uploaded_image_path,
                    product["image_path"]
                )
                if gemini_result["success"]:
                    visual_similarity = gemini_result["similarity"]
            except Exception as e:
                print(f"Visual comparison failed: {e}")
                visual_similarity = 0

        # Combined similarity (60% visual, 40% text for products with images)
        if visual_similarity > 0:
            combined_similarity = round((visual_similarity * 0.6) + (text_similarity * 0.4), 1)
        else:
            combined_similarity = text_similarity

        if combined_similarity >= 50:
            product_with_similarity = product.copy()
            product_with_similarity["similarity"] = combined_similarity
            product_with_similarity["text_similarity"] = text_similarity
            product_with_similarity["visual_similarity"] = visual_similarity
            similar_products.append(product_with_similarity)

    # Sort by combined similarity
    similar_products.sort(key=lambda x: x["similarity"], reverse=True)

    return similar_products
