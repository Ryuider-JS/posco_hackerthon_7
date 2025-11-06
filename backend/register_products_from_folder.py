#!/usr/bin/env python3
"""
product_list_picture 폴더의 제품들을 DB에 자동 등록
각 Q-CODE당 대표 이미지 1장씩 등록
"""
import os
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(__file__))

from app.database import Base
from app.models.product import Product

# 설정
PRODUCT_LIST_DIR = "../product_list_picture"
DATABASE_URL = "sqlite:///./qcode.db"

def register_products():
    """
    product_list_picture의 제품들을 DB에 등록
    """
    # DB 파일이 존재하는지 확인하고 재생성
    db_file = "qcode.db"
    if os.path.exists(db_file):
        print(f"[*] Using existing database: {db_file}")
    else:
        print(f"[*] Creating new database: {db_file}")

    # DB 연결
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    product_list_path = Path(PRODUCT_LIST_DIR)

    if not product_list_path.exists():
        print(f"[ERROR] Directory not found: {product_list_path}")
        return False

    print("=" * 60)
    print("  Product Registration from product_list_picture")
    print("=" * 60)
    print()

    registered_count = 0
    skipped_count = 0

    # Q-CODE 폴더 순회
    for qcode_dir in sorted(product_list_path.iterdir()):
        if not qcode_dir.is_dir():
            continue

        qcode = qcode_dir.name
        print(f"[*] Processing Q-CODE: {qcode}")

        # 이미 DB에 있는지 확인
        existing = db.query(Product).filter(Product.qcode == qcode).first()
        if existing:
            print(f"    [SKIP] Already exists in database")
            skipped_count += 1
            continue

        # 첫 번째 이미지 찾기 (origin 제외)
        images = []
        for img_file in sorted(qcode_dir.iterdir()):
            if not img_file.is_file():
                continue
            if "origin" in img_file.name.lower():
                continue
            if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                images.append(img_file)

        if not images:
            print(f"    [ERROR] No valid images found")
            continue

        # 대표 이미지 선택 (첫 번째)
        representative_image = images[0]
        image_path = str(representative_image.absolute()).replace('\\', '/')

        print(f"    Representative image: {representative_image.name}")
        print(f"    Total images available: {len(images)}")

        # 제품 정보 자동 생성
        # Q-CODE에서 기본 정보 추출
        name = f"제품 {qcode}"
        category = "미분류"
        description = f"product_list_picture/{qcode}에서 자동 등록됨"

        # DB에 제품 등록
        new_product = Product(
            qcode=qcode,
            name=name,
            category=category,
            description=description,
            image_path=image_path,
            diameter=None,
            length=None,
            material=None,
            specs=f"이미지 {len(images)}장 보유",
            last_price=0.0,
            purchase_count=0,
            average_rating=0.0,
            current_stock=0
        )

        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        print(f"    [OK] Registered successfully")
        print(f"        Name: {name}")
        print(f"        Image: {image_path}")
        print(f"        Available images: {len(images)} files")
        print()

        registered_count += 1

    print("=" * 60)
    print(f"  Registration Complete!")
    print(f"    Registered: {registered_count} products")
    print(f"    Skipped: {skipped_count} products (already exist)")
    print("=" * 60)
    print()

    if registered_count > 0:
        print("[*] Next steps:")
        print("    1. Test CLIP similarity search:")
        print("       curl -X POST http://localhost:8000/api/analyze-image \\")
        print("         -F \"file=@product_list_picture/Q1208172/Q1208172_2.png\"")
        print()
        print("    2. View registered products:")
        print("       curl http://localhost:8000/api/products")
        print()

    db.close()
    return True

if __name__ == "__main__":
    register_products()
