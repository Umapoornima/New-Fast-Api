import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, root_validator


class PromptCreate(BaseModel):
    name: str
    prompt: str


class PromptUpdate(BaseModel):
    name: Optional[str] = None
    prompt: Optional[str] = None

    @root_validator(pre=True)
    def at_least_one_field(cls, values):
        if not any(values.get(field) for field in ['name', 'prompt']):
            raise ValueError(
                'At least one field (name or prompt) must be provided.')
        return values


class PromptRead(PromptCreate):
    id: int

    class Config:
        from_attributes = True


class ImageComparisonCreate(BaseModel):
    guid: Optional[str] = None
    product_image: Optional[str] = None
    captured_image: Optional[str] = None
    confidence_level: Optional[str] = None
    result: Optional[str] = None
    product_1: Optional[str] = None
    product_2: Optional[str] = None
    explanation: Optional[str] = None
    

    class Config:
        from_attributes = True


class ImageComparisonUpdate(BaseModel):
    product_image: Optional[str] = None
    captured_image: Optional[str] = None
    confidence_level: Optional[str] = None
    result: Optional[str] = None
    product_1: Optional[str] = None
    product_2: Optional[str] = None
    explanation: Optional[str] = None

    class Config:
        from_attributes = True


class ImageComparisonRead(BaseModel):
    id: int
    guid: str
    product_image: str
    captured_image: str
    confidence_level: Optional[str] = None
    result: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None
    product_1: Optional[str] = None
    product_2: Optional[str] = None
    explanation: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True



class BillOfLadingInventoryComparisonBase(BaseModel):
    bill_of_lading_image: Optional[str] = None
    inventory_item_image: Optional[str] = None
    ai_response: Optional[str] = None
    status: Optional[str] = None
    guid: Optional[str] = str(uuid.uuid4())  
    error: Optional[str] = None 


class BillOfLadingInventoryComparisonCreate(BillOfLadingInventoryComparisonBase):
    pass


class BillOfLadingInventoryComparison(BillOfLadingInventoryComparisonBase):
    id: int
    CreatedAt: datetime

    class Config:
        orm_mode = True