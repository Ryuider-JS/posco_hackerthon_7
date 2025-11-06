#!/usr/bin/env python3
"""
등록된 제품 확인 및 검증
"""
import sys
sys.path.insert(0, '.')
from app.database import SessionLocal
from app.models.product import Product

def verify_products():
    """등록된 제품 목록 확인"""
    db = SessionLocal()

    try:
        products = db.query(Product).all()

        print("=" * 80)
        print(f"등록된 제품: 총 {len(products)}개")
        print("=" * 80)
        print()

        # Roboflow 학습 대상 제품 찾기
        tangerine = db.query(Product).filter(Product.qcode == "TANGERINE-001").first()
        egg = db.query(Product).filter(Product.qcode == "EGG-001").first()

        print("[Roboflow 학습 대상 제품]")
        print()

        if tangerine:
            print(f"1. TANGERINE-001 - {tangerine.name}")
            print(f"   제조사: {tangerine.manufacturer}")
            print(f"   카테고리: {tangerine.category}")
            print(f"   이미지: {tangerine.image_path}")
            print()
        else:
            print("[ERROR] TANGERINE-001 제품이 등록되지 않았습니다!")
            print()

        if egg:
            print(f"2. EGG-001 - {egg.name}")
            print(f"   제조사: {egg.manufacturer}")
            print(f"   카테고리: {egg.category}")
            print(f"   이미지: {egg.image_path}")
            print()
        else:
            print("[ERROR] EGG-001 제품이 등록되지 않았습니다!")
            print()

        print("=" * 80)
        print("[전체 제품 목록]")
        print("=" * 80)
        print()

        for idx, product in enumerate(products, 1):
            print(f"{idx}. {product.qcode} - {product.name}")
            if product.manufacturer:
                print(f"   제조사: {product.manufacturer}")
            if product.category:
                print(f"   카테고리: {product.category}")
            print()

        print("=" * 80)
        print("[Roboflow 클래스 매핑]")
        print("=" * 80)
        print()
        print('CLASS_NAME_TO_QCODE = {')
        print('    "Tangerine": "TANGERINE-001",')
        print('    "Egg": "EGG-001",')
        print('}')
        print()

        # 매핑 검증
        if tangerine and egg:
            print("[OK] Roboflow 모델이 감지하는 두 제품이 모두 DB에 등록되었습니다!")
        else:
            print("[WARNING] 일부 제품이 등록되지 않았습니다.")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_products()
