# this is old file 
# this file uses postgress database for invoice analysis 
# this api is currently used by viziapps demo 1 and ddemo 2


import base64
import json
import os
import uuid
from typing import List, Optional

import anthropic
import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.basic_auth import Authenticate
from app.database.database import get_db
from app.model.model import ImageAnalysis, Prompt

router = APIRouter(
    prefix="/api/v1/analyze_invoice",
    tags=['Image Analysis'],
    dependencies=[Depends(Authenticate)],
)

client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])


class Payload(BaseModel):
  image_url: str
  # questions: List[str]
  questions: Optional[List[str]] = []
  prompt_id: Optional[int] = 1


def analyze(data, db):

  instance = data.get('instance')
  # questions = data.get('questions')
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
                    # "text": f"{prompt}, :\n\n" + '\n'.join(questions),
                    "text": f"{prompt}, :\n\n"
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

    instance.status = "SUCCESS"
    instance.response = json_str
    db.commit()
  except Exception as e:
    instance.status = "ERROR"
    instance.error = str(e)
    db.commit()
    pass


@router.post('')
def analyze_invoice(request: Request,
                    payload: Payload,
                    background_tasks: BackgroundTasks,
                    db: Session = Depends(get_db)):
  image_url = payload.image_url
  questions = payload.questions
  prompt_id = payload.prompt_id

  prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()

  if prompt is None:
    raise HTTPException(status_code=404, detail="Invalid Promt ID")

  # instance = db.query(ImageAnalysis).filter(
  #     ImageAnalysis.image_url == image_url).first()

  # if not instance:

  try:

    data = {
        "guid": str(uuid.uuid4()),
        "image_url": image_url,
        "status": "PENDING"
    }

    instance = ImageAnalysis(**dict(data))
    db.add(instance)
    db.commit()
    db.refresh(instance)
  except Exception as e:
    raise HTTPException(status_code=400, detail=f"{e}") from None

  data = {
      "image_url": image_url,
      "questions": questions,
      "instance_id": instance.id,
      "instance": instance,
      "prompt": prompt.prompt,
  }

  background_tasks.add_task(analyze, data, db)

  base_url = str(request.base_url)

  full_url = f"{base_url}api/v1/analyze_invoice/{instance.guid}"

  return {"url": full_url, "guid": instance.guid}


@router.get('/{guid}')
def get(guid, db: Session = Depends(get_db)):
  instance = db.query(ImageAnalysis).filter(ImageAnalysis.guid == guid).first()
  if not instance:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Instance with guid {guid} not found")

  try:
    response = json.loads(instance.response if instance.response else "{}")
  except ValueError:
    response = ""

  instance_dict = {
      "id": instance.id,
      "guid": instance.guid,
      "image_url": instance.image_url,
      "status": instance.status,
      "error": instance.error,
      "created_at": instance.created_at,
      "updated_at": instance.updated_at,
      "response": response,
  }

  return instance_dict
