from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import random
import string

def generate_qcode():
    """Generate unique Q-CODE in format Q-XXXX-YYYY"""
    timestamp = datetime.now().strftime("%y%m")
    random_suffix = ''.join(random.choices(string.digits, k=4))
    return f"Q-{timestamp}-{random_suffix}"

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    qcode = Column(String, unique=True, index=True, default=generate_qcode)
    name = Column(String, nullable=False)
    category = Column(String, default="미분류")
    description = Column(Text)
    image_path = Column(String)

    # Spec fields for text-based search
    diameter = Column(String)  # 직경
    length = Column(String)    # 길이
    material = Column(String)  # 재질
    specs = Column(Text)       # Additional specs in text format

    # Purchase history
    purchase_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    last_price = Column(Float, default=0.0)

    # Inventory management (재고 관리)
    current_stock = Column(Integer, default=0)          # 현재 재고 수량
    min_stock = Column(Integer, default=10)             # 최소 재고 (경고 기준)
    max_stock = Column(Integer, default=100)            # 최대 재고
    reorder_point = Column(Integer, default=20)         # 재주문 시점
    stock_unit = Column(String, default="개")           # 재고 단위
    low_stock_alert = Column(Boolean, default=True)     # 재고 부족 알림 활성화

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    history = relationship("InventoryHistory", back_populates="product", cascade="all, delete-orphan")

    def to_dict(self, for_api=True):
        # Convert absolute image path to relative URL for frontend
        image_url = self.image_path

        # Only convert to relative path if this is for API response
        if for_api and image_url:
            # Convert Windows backslashes to forward slashes
            image_url = image_url.replace("\\", "/")

            # Extract path after "product_list_picture/"
            if "product_list_picture/" in image_url:
                relative_path = image_url.split("product_list_picture/")[1]
                image_url = f"product_list_picture/{relative_path}"
            # Extract path after "uploads/"
            elif "uploads/" in image_url:
                relative_path = image_url.split("uploads/")[1]
                image_url = f"uploads/{relative_path}"

        return {
            "id": self.id,
            "qcode": self.qcode,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "image_path": image_url,
            "diameter": self.diameter,
            "length": self.length,
            "material": self.material,
            "specs": self.specs,
            "purchase_count": self.purchase_count,
            "average_rating": self.average_rating,
            "last_price": self.last_price,
            "current_stock": self.current_stock,
            "min_stock": self.min_stock,
            "max_stock": self.max_stock,
            "reorder_point": self.reorder_point,
            "stock_unit": self.stock_unit,
            "low_stock_alert": self.low_stock_alert,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
