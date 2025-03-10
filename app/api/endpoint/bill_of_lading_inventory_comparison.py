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
from app.model.model import BillOfLadingInventoryComparison, Prompt
from app.schemas.schemas import (
    BillOfLadingInventoryComparison as BillOfLadingInventoryComparisonRead, )

router = APIRouter(
    prefix="/api/v1/bill_of_lading_inventory_comparison",
    tags=['bill_of_lading_inventory_comparison'],
    dependencies=[Depends(Authenticate)],
)

Base = declarative_base()

client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])


class Payload(BaseModel):
    bill_of_lading_image: str
    inventory_image: str
    prompt_id: int


def analyze(data, db):

    instance = data.get('instance')
    bill_of_lading_image = data.get('bill_of_lading_image')
    inventory_image = data.get('inventory_image')
    prompt = data.get('prompt')
    image_media_type = "image/jpeg"

    try:
        image_response = httpx.get(bill_of_lading_image)
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
        image_response = httpx.get(inventory_image)
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
                    "text": prompt,
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

        instance.ai_response = json_str
        json_str = json.loads(json_str)

        instance.status = "SUCCESS"

        db.commit()

    except Exception as e:
        instance.error = str(e)
        instance.status = "ERROR"
        db.commit()
        print("error bro", e)
        pass


@router.post('')
def compare_shipping_inventory(request: Request,
                               payload: Payload,
                               background_tasks: BackgroundTasks,
                               db: Session = Depends(get_db)):

    bill_of_lading_image = payload.bill_of_lading_image
    inventory_image = payload.inventory_image
    prompt_id = payload.prompt_id

    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()

    if prompt is None:
        raise HTTPException(status_code=404, detail="Invalid Prompt ID")

    try:
        data = {
            "guid": str(uuid.uuid4()),
            "bill_of_lading_image": bill_of_lading_image,
            "inventory_item_image": inventory_image,
            "status": "PENDING"
        }

        instance = BillOfLadingInventoryComparison(**dict(
            data))  # Update model usage
        db.add(instance)
        db.commit()
        db.refresh(instance)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}") from None

    data = {
        "bill_of_lading_image": bill_of_lading_image,
        "inventory_image": inventory_image,
        "instance": instance,
        "prompt": prompt.prompt,
    }

    background_tasks.add_task(analyze, data, db)

    base_url = str(request.base_url)
    full_url = f"{base_url}api/v1/bill_of_lading_inventory_comparison/{instance.guid}"

    return {"url": full_url, "id": instance.id, "guid": instance.guid}


@router.get("/{guid}", response_model=BillOfLadingInventoryComparisonRead)
def read_item(guid: str, db: Session = Depends(get_db)):
    instance = db.query(BillOfLadingInventoryComparison).filter(
        BillOfLadingInventoryComparison.guid == guid).first()
    if instance is None:
        raise HTTPException(status_code=404, detail="Instance not found")
    return instance


# https://viziappsstandardprob927.blob.core.windows.net/mobifleximages/beta/255mmsingleventedfrontbrakediscforvauxhallastramk4astragp24973101_image.jpg?sv=2021-04-10&se=2034-10-03T10:58:46Z&sr=c&sp=racwdxltfi&sig=xzUvyaZznMh81kKqFaNKbjmqbpS49nUsuHsypGuHz1Q%3D
# https://viziappsstandardprob927.blob.core.windows.net/mobifleximages/beta/Bill_of_Lading__Vented_Disk.png?sv=2021-04-10&se=2034-10-03T10:59:08Z&sr=c&sp=racwdxltfi&sig=uXezA34pfOzj8t2F%2BTwP6sCJCl0wVPDzJosO8gE8Dmk%3Dimport base64
