import os
import base64
from openai import OpenAI
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

def get_openai_client():
    """Get OpenAI client instance"""
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def encode_image_to_base64(image_path: str) -> str:
    """Encode image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_product_image(image_path: str) -> Dict:
    """
    Analyze product image using OpenAI Vision API
    Returns product characteristics and extracted information
    """
    try:
        base64_image = encode_image_to_base64(image_path)
        client = get_openai_client()

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """이 제품 이미지를 분석하여 다음 정보를 추출해주세요:

1. 제품명 (가능한 구체적으로)
2. 카테고리 (예: 기계부품, 체결부품, 전자부품 등)
3. 재질 (예: 스테인리스, 철, 플라스틱 등)
4. 크기/치수 (추정 가능한 경우)
5. 주요 특징 및 용도
6. 검색 키워드 (유사 제품 검색에 사용할 수 있는 키워드들)

JSON 형식으로 응답해주세요:
{
    "name": "제품명",
    "category": "카테고리",
    "material": "재질",
    "dimensions": "크기/치수",
    "description": "상세 설명",
    "keywords": ["키워드1", "키워드2", ...]
}"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000,
            temperature=0.3
        )

        result = response.choices[0].message.content

        # Try to parse JSON response
        import json
        try:
            parsed_result = json.loads(result)
            return {
                "success": True,
                "analysis": parsed_result,
                "raw_text": result
            }
        except json.JSONDecodeError:
            return {
                "success": True,
                "analysis": None,
                "raw_text": result
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "raw_text": f"이미지 분석 중 오류 발생: {str(e)}"
        }

def analyze_with_specs(specs_text: str) -> Dict:
    """
    Analyze product based on text specifications
    """
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": f"""다음 제품 스펙/설명을 분석하여 구조화된 정보를 추출해주세요:

입력: {specs_text}

JSON 형식으로 응답해주세요:
{{
    "name": "제품명",
    "category": "카테고리",
    "material": "재질",
    "dimensions": "크기/치수",
    "description": "상세 설명",
    "keywords": ["키워드1", "키워드2", ...]
}}"""
                }
            ],
            max_tokens=800,
            temperature=0.3
        )

        result = response.choices[0].message.content

        import json
        try:
            parsed_result = json.loads(result)
            return {
                "success": True,
                "analysis": parsed_result,
                "raw_text": result
            }
        except json.JSONDecodeError:
            return {
                "success": True,
                "analysis": None,
                "raw_text": result
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "raw_text": f"스펙 분석 중 오류 발생: {str(e)}"
        }

def calculate_similarity(product1: Dict, product2: Dict, analysis_data: Dict = None) -> float:
    """
    Calculate similarity between two products
    Returns a score between 0-100
    """
    score = 0.0
    max_score = 0.0

    # Name similarity (weight: 30)
    if product1.get("name") and product2.get("name"):
        max_score += 30
        name1 = product1["name"].lower()
        name2 = product2["name"].lower()
        if name1 == name2:
            score += 30
        elif name1 in name2 or name2 in name1:
            score += 20
        else:
            # Check for common words
            words1 = set(name1.split())
            words2 = set(name2.split())
            common = len(words1 & words2)
            if common > 0:
                score += min(15, common * 5)

    # Material similarity (weight: 25)
    if product1.get("material") and product2.get("material"):
        max_score += 25
        if product1["material"].lower() == product2["material"].lower():
            score += 25
        elif product1["material"].lower() in product2["material"].lower() or \
             product2["material"].lower() in product1["material"].lower():
            score += 15

    # Category similarity (weight: 20)
    if product1.get("category") and product2.get("category"):
        max_score += 20
        if product1["category"].lower() == product2["category"].lower():
            score += 20
        elif product1["category"].lower() in product2["category"].lower() or \
             product2["category"].lower() in product1["category"].lower():
            score += 10

    # Dimensions similarity (weight: 15)
    if product1.get("diameter") and product2.get("diameter"):
        max_score += 10
        if product1["diameter"] == product2["diameter"]:
            score += 10

    if product1.get("length") and product2.get("length"):
        max_score += 5
        if product1["length"] == product2["length"]:
            score += 5

    # Description/specs similarity (weight: 10)
    if product1.get("description") and product2.get("description"):
        max_score += 10
        desc1_words = set(product1["description"].lower().split())
        desc2_words = set(product2["description"].lower().split())
        common = len(desc1_words & desc2_words)
        if common > 0:
            score += min(10, common * 1)

    # Calculate final percentage
    if max_score > 0:
        return round((score / max_score) * 100, 1)
    return 0.0

def compare_with_existing_products(analysis: Dict, existing_products: List[Dict]) -> List[Dict]:
    """
    Compare analyzed product with existing products in database
    Returns list of similar products with similarity scores
    """
    similar_products = []

    for product in existing_products:
        similarity = calculate_similarity(analysis, product, analysis)

        if similarity >= 50:  # Only include products with >50% similarity
            product_with_similarity = product.copy()
            product_with_similarity["similarity"] = similarity
            similar_products.append(product_with_similarity)

    # Sort by similarity (highest first)
    similar_products.sort(key=lambda x: x["similarity"], reverse=True)

    return similar_products
