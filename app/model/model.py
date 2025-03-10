import uuid

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class ImageAnalysis(Base):
  __tablename__ = "image_analysis"

  id = Column(Integer, primary_key=True, index=True)
  guid = Column(String(128), default=uuid.uuid4, unique=True, nullable=False)
  image_url = Column(String(128),nullable=True)
  status = Column(String(128),nullable=True)
  response = Column(Text,nullable=True)
  error = Column(Text,nullable=True)
  created_at = Column(DateTime, default=func.now())
  updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Prompt(Base):
  __tablename__ = "prompts"

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, nullable=False)
  prompt = Column(Text, nullable=False)



class ImageComparison(Base):
  __tablename__ = 'image_comparisons'
  id = Column(Integer, primary_key=True, index=True)
  guid = Column(String(128), default=uuid.uuid4, unique=True, nullable=False)
  product_image = Column(String, nullable=False)
  captured_image = Column(String, nullable=False)
  confidence_level = Column(String(255))
  result = Column(String(255))
  product_1 = Column(Text)
  product_2 = Column(Text)
  explanation = Column(Text)
  created_at = Column(DateTime, default=func.now())
  updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
  status = Column(String(255))
  response = Column(Text)
  error = Column(Text)

  @property
  def guid_str(self):
      return str(self.guid)




class ShippingDocuments(Base):
  __tablename__ = "shipping_documents"

  id = Column(Integer, primary_key=True, index=True)
  guid = Column(String(128), default=uuid.uuid4, unique=True, nullable=False)
  document_image = Column(String(128),nullable=True)
  status = Column(String(128),nullable=True)
  ai_response = Column(Text,nullable=True)
  error = Column(Text,nullable=True)
  created_at = Column(DateTime, default=func.now())
  updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
  enterprise_shipping_policy_status = Column(String(128),nullable=True)
  decision_criteria = Column(Text,nullable=True)
  product_type = Column(String(128),nullable=True)
  additional_info = Column(Text,nullable=True)

  @property
  def guid_str(self):
      return str(self.guid)



class BillOfLadingInventoryComparison(Base):
  __tablename__ = 'bill_of_lading_inventory_comparison'

  id = Column(Integer, primary_key=True, index=True)
  bill_of_lading_image = Column(Text, nullable=True)
  inventory_item_image = Column(Text, nullable=True)
  ai_response = Column(Text, nullable=True)
  status = Column(String(50), nullable=True)
  guid = Column(String(255), default=str(uuid.uuid4()), unique=True, nullable=False)
  error = Column(Text, nullable=True)
  CreatedAt = Column(DateTime, default=func.now())





class HazWaste(Base):
  __tablename__ = "haz_waste"

  id = Column(Integer, primary_key=True, index=True)
  guid = Column(String(128), default=uuid.uuid4, unique=True, nullable=False)
  document_image = Column(String(128),nullable=True)
  status = Column(String(128),nullable=True)
  ai_response = Column(Text,nullable=True)
  error = Column(Text,nullable=True)
  created_at = Column(DateTime, default=func.now())
  updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
  user_action = Column(Text,nullable=True)
  is_haz_waste = Column(String(50),nullable=True)
  explanation = Column(Text,nullable=True)
  
  @property
  def guid_str(self):
      return str(self.guid)