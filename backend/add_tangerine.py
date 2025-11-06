#!/usr/bin/env python3
"""
TANGERINE-001 제품을 DB에 수동 등록
"""
import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '.')
from app.database import SessionLocal
from app.models.product import Product

def add_tangerine():
    """TANGERINE-001 제품 등록"""
    db = SessionLocal()

    try:
        # 이미 등록되어 있는지 확인
        existing = db.query(Product).filter(Product.qcode == "TANGERINE-001").first()
        if existing:
            print("TANGERINE-001이 이미 등록되어 있습니다.")
            print(f"제품명: {existing.name}")
            return

        # 이미지 경로
        image_path = str(Path("../product_list_picture/TANGERINE-001/tangerine-sample.png").absolute()).replace('\\', '/')

        # TANGERINE-001 제품 생성
        tangerine = Product(
            qcode="TANGERINE-001",
            name="탄제린 (귤)",
            category="식품",
            description="제주산 프리미엄 탄제린",
            image_path=image_path,
            diameter=None,
            length=None,
            material=None,
            specs="탄제린,프리미엄,제주산,당도 12Brix 이상",
            n2b_product_code="20001111",
            standard_name="탄제린 (귤)",
            model_name="TANGERINE-PREMIUM",
            manufacturer="제주감귤농협",
            sourcing_group="식품/음료",
            leaf_class="과일류",
            attributes=json.dumps({
                "원산지": "제주도",
                "등급": "특",
                "당도": "12Brix 이상",
                "크기": "중과"
            }, ensure_ascii=False),
            last_order_date=datetime.strptime("2024-10-28", "%Y-%m-%d"),
            next_predicted_purchase_date=datetime.strptime("2024-12-15", "%Y-%m-%d"),
            avg_purchase_interval_days=48.0,
            last_price=45000.0,
            purchase_count=56,
            average_rating=0.0,
            current_stock=0
        )

        db.add(tangerine)
        db.commit()
        db.refresh(tangerine)

        print("[OK] TANGERINE-001 등록 완료!")
        print(f"   제품명: {tangerine.name}")
        print(f"   제조사: {tangerine.manufacturer}")
        print(f"   카테고리: {tangerine.category}")
        print(f"   이미지: {tangerine.image_path}")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] 에러 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    add_tangerine()
