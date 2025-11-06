from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class InventoryHistory(Base):
    """재고 변동 이력 테이블"""
    __tablename__ = "inventory_history"

    id = Column(Integer, primary_key=True, index=True)
    qcode = Column(String, ForeignKey("products.qcode"), nullable=False, index=True)

    # 재고 정보
    quantity = Column(Integer, nullable=False)          # 감지된 수량
    quantity_change = Column(Integer, default=0)        # 이전 대비 변화량
    detection_confidence = Column(Float, default=0.0)   # 감지 신뢰도

    # 메타데이터
    detection_method = Column(String, default="webcam_scan")  # "webcam_scan", "manual_adjustment" 등
    frame_path = Column(String)                         # 감지 당시 프레임 이미지 경로 (선택)
    notes = Column(Text)                                # 메모

    # 타임스탬프
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)

    # Relationship
    product = relationship("Product", back_populates="history")

    def to_dict(self):
        return {
            "id": self.id,
            "qcode": self.qcode,
            "quantity": self.quantity,
            "quantity_change": self.quantity_change,
            "detection_confidence": self.detection_confidence,
            "detection_method": self.detection_method,
            "frame_path": self.frame_path,
            "notes": self.notes,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
