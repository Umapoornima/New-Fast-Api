# this is new file 
# this file uses sql server database for invoice analysis 
# this api is currently used by viziapps demo 1 and ddemo 2

import base64
import json
import os
import uuid

import anthropic
import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.basic_auth import Authenticate
from app.database.sqlserver import get_db
from app.model.model import Prompt, HazWaste
from app.utils.ITAR_policies import ITAR_policies

router = APIRouter(
    prefix="/api/v2/haz_waste_analysis",
    tags=['HAZ WASTE ANALYSIS'],
    dependencies=[Depends(Authenticate)],
)

client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])


class Payload(BaseModel):
  image_url: str
  prompt_id: int


def analyze(data, db):

  instance = data.get('instance')
  image_url = data.get('image_url')
  prompt = data.get('prompt')
  image_media_type = "image/jpeg"

  try:
    image_response = httpx.get(image_url)
    if image_response.status_code == 200:
      image_data = image_response.content
      image_base64 = base64.b64encode(image_data).decode('utf-8')
    else:
      instance.status = "ERROR"
      instance.error = f"Image not found status_code = {image_response.status_code}"
      db.commit()
      return
  except Exception as e:
    instance.status = "ERROR"
    instance.error = str(e)
    db.commit()
    return

  try:
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[{
            "role":
            "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": image_media_type,
                        "data": image_base64,
                    },
                },
                {
                    "type": "text",
                    "text": f'''
                    {prompt}:\n\n  
                    Give response in JSON using key value pairs
                    use two keys 
                    1.isHazardousMaterial : Yes/No
                    2.explanation
                    '''
                }
            ],
        }],
    )

    response = ""
    for res in message.content[0]:
      response = res[-1]
      break

    json_str = response.split("{", 1)[1].rsplit("}", 1)[0]
    json_str = "{" + json_str + "}"
    json_str = json_str.replace("'", "")
    
    instance.ai_response = json_str
    
    json_str = json.loads(json_str)

    instance.status = "SUCCESS"
    instance.is_haz_waste = json_str.get(
      "isHazardousMaterial" ,"")
    instance.explanation = json_str.get("explanation", "")
    # instance.product_type = json_str.get("product_type", "")
    # instance.additional_info = json_str.get("additional_info", "")
    db.commit()
  except Exception as e:
    instance.status = "ERROR"
    instance.error = str(e)
    db.commit()
    pass


@router.post('')
def analyze_haz_waste(request: Request,
                    payload: Payload,
                    background_tasks: BackgroundTasks,
                    db: Session = Depends(get_db)):
  image_url = payload.image_url
  prompt_id = payload.prompt_id

  

  prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()

  if prompt is None:
    raise HTTPException(status_code=404, detail="Invalid Promt ID")

  try:

    data = {
        "guid": str(uuid.uuid4()),
        "document_image": image_url,
        "status": "PENDING"
    }

    instance = HazWaste(**dict(data))
    db.add(instance)
    db.commit()
    db.refresh(instance)
  except Exception as e:
    raise HTTPException(status_code=400, detail=f"{e}") from None

  data = {
      "image_url": image_url,
      "instance": instance,
      "prompt": prompt.prompt,
  }

  background_tasks.add_task(analyze, data, db)

  # base_url = str(request.base_url)

  # full_url = f"{base_url}api/v1/analyze_invoice/{instance.guid}"

  return {"id": instance.id ,"guid":instance.guid}  
 



@router.get('/{guid}')
def get(guid, db: Session = Depends(get_db)):
  instance = db.query(HazWaste).filter_by(guid=guid).first()
  if not instance:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Instance with guid {guid} not found")

  try:
    response = json.loads(instance.ai_response if instance.ai_response else "{}")
  except ValueError:
    response = {}

  instance_dict = {
      "id": instance.id,
      "guid": instance.guid,
      "document_image": instance.document_image,
      "status": instance.status,
      "error": instance.error,
      "created_at": instance.created_at,
      "updated_at": instance.updated_at,
      "ai_response": response,
      "user_action": instance.user_action,
      "isHazardousMaterial" : instance.is_haz_waste,    
      "explanation" : instance.explanation

  }

  return instance_dict






class HazWasteUpdateRequest(BaseModel):
  user_explanation: str

@router.put('/{guid}')
def update_haz_waste(guid: str, request: HazWasteUpdateRequest, db: Session = Depends(get_db)):
 
  instance = db.query(HazWaste).filter_by(guid=guid).first()

  if not instance:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                          detail=f"Instance with guid {guid} not found")

  
  instance.user_action = request.user_explanation
  

 
  db.commit()
  db.refresh(instance)

  return {
      "message": "HazWaste instance updated successfully",
      "id": instance.id,
      "guid": instance.guid,
      "is_haz_waste": instance.is_haz_waste,
      "explanation": instance.explanation
  }
