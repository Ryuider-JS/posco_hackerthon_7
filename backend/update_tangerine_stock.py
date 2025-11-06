#!/usr/bin/env python3
"""
TANGERINE-001 제품의 최소 재고를 5로 업데이트
"""
import sys
sys.path.insert(0, '.')
from app.database import SessionLocal
from app.models.product import Product

def update_tangerine_min_stock():
    """TANGERINE-001의 최소 재고를 5로 설정"""
    db = SessionLocal()

    try:
        # TANGERINE-001 제품 찾기
        tangerine = db.query(Product).filter(Product.qcode == "TANGERINE-001").first()

        if not tangerine:
            print("[ERROR] TANGERINE-001 제품을 찾을 수 없습니다!")
            return

        # 이전 값 저장
        old_min_stock = tangerine.min_stock
        old_reorder_point = tangerine.reorder_point

        # 최소 재고를 5로 업데이트
        tangerine.min_stock = 5

        # 재주문 시점도 함께 조정 (최소 재고보다 높게 설정)
        if tangerine.reorder_point <= 5:
            tangerine.reorder_point = 10  # 재주문 시점을 10으로 설정

        db.commit()
        db.refresh(tangerine)

        print("=" * 80)
        print("[OK] TANGERINE-001 재고 설정 업데이트 완료!")
        print("=" * 80)
        print(f"제품명: {tangerine.name}")
        print(f"Q-CODE: {tangerine.qcode}")
        print(f"\n[재고 설정 변경]")
        print(f"  최소 재고: {old_min_stock} → {tangerine.min_stock}")
        print(f"  재주문 시점: {old_reorder_point} → {tangerine.reorder_point}")
        print(f"  현재 재고: {tangerine.current_stock}")
        print(f"  최대 재고: {tangerine.max_stock}")
        print("=" * 80)

        # 재고 상태 표시
        if tangerine.current_stock <= tangerine.min_stock:
            print("[경고] 현재 재고가 최소 재고 이하입니다! (Critical)")
        elif tangerine.current_stock <= tangerine.reorder_point:
            print("[주의] 재주문이 필요합니다! (Warning)")
        else:
            print("[안전] 재고가 충분합니다.")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] 에러 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    update_tangerine_min_stock()
