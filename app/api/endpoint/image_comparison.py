import base64
import json
import os
import uuid

import anthropic
import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from app.basic_auth import Authenticate
from app.database.sqlserver import get_db
from app.model.model import ImageComparison, Prompt
from app.schemas.schemas import ImageComparisonRead

router = APIRouter(
    prefix="/api/v1/image_comparison",
    tags=['image_comparison'],
    dependencies=[Depends(Authenticate)],
)

Base = declarative_base()

client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])


class Payload(BaseModel):
    product_image: str
    captured_image: str
    prompt_id: int




def analyze(data, db):
    print("111")

    instance = data.get('instance')
    image_url_1 = data.get('product_image')
    image_url_2 = data.get('captured_image')
    prompt = data.get('prompt')
    image_media_type = "image/jpeg"

    try:
        image_response = httpx.get(image_url_1)
        if image_response.status_code == 200:
            image_data = image_response.content
            image_base64_1 = base64.b64encode(image_data).decode('utf-8')
        else:
            return
    except Exception as e:
        instance.error = str(e)
        instance.status = "ERROR"
        db.commit()
        print("error 1")
        return

    try:
        image_response = httpx.get(image_url_2)
        if image_response.status_code == 200:
            image_data = image_response.content
            image_base64_2 = base64.b64encode(image_data).decode('utf-8')
        else:
            return
    except Exception as e:
        instance.error = str(e)
        instance.status = "ERROR"
        db.commit()
        print("error 2")
        return

    try:
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=[{
                "role":
                "user",
                "content": [{
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": image_media_type,
                        "data": image_base64_1,
                    },
                }, {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": image_media_type,
                        "data": image_base64_2,
                    },
                }, {
                    "type": "text",
                    "text": f"{prompt}, :\n\n"
                }],
            }],
        )

        response = ""
        for res in message.content[0]:
            response = res[-1]
            break

        json_str = response.split("{", 1)[1].rsplit("}", 1)[0]
        json_str = "{" + json_str + "}"
        json_str = json_str.replace("'", "")
        
        instance.response = json_str
        json_str = json.loads(json_str)

        instance.confidence_level = json_str.get("confidence_level","")
        instance.product_1 = str(json_str.get("product_1",""))
        instance.product_2 = str(json_str.get("product_2",""))
        instance.explanation = json_str.get("explanation","")
        instance.result = json_str.get("result","")
        instance.status = "SUCCESS"

        db.commit()

    except Exception as e:
        instance.error = str(e)
        instance.status = "ERROR"
        db.commit()
        print("error bro", e)
        pass


@router.post('')
def compare_image(request: Request,
                  payload: Payload,
                  background_tasks: BackgroundTasks,
                  db: Session = Depends(get_db)):

    product_image = payload.product_image
    captured_image = payload.captured_image
    prompt_id = payload.prompt_id

    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()

    if prompt is None:
        raise HTTPException(status_code=404, detail="Invalid Promt ID")

    try:

        data = {
            "guid": str(uuid.uuid4()),
            "product_image": product_image,
            "captured_image": captured_image,
            "status": "PENDING"
        }

        print("data", data)

        instance = ImageComparison(**dict(data))
        db.add(instance)
        db.commit()
        db.refresh(instance)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}") from None

    data = {
        "product_image": product_image,
        "captured_image": captured_image,
        "instance": instance,
        "prompt": prompt.prompt,
    }

    background_tasks.add_task(analyze, data, db)
    # analyze(data, db)

    base_url = str(request.base_url)

    full_url = f"{base_url}api/v1/image_comparison/{instance.guid}"

    return {"url": full_url, "id":instance.id, "guid": instance.guid}


@router.get("/{guid}", response_model=ImageComparisonRead)
def read_item(guid: str, db: Session = Depends(get_db)):

    print("guid", guid)
    instance = db.query(ImageComparison).filter(
        ImageComparison.guid == guid).first()
    if instance is None:
        raise HTTPException(status_code=404, detail="instance not found")
    return instance
