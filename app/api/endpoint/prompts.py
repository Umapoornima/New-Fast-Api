from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.basic_auth import Authenticate
from app.database.database import get_db
from app.model.model import Prompt
from app.schemas.schemas import PromptCreate, PromptRead, PromptUpdate

router = APIRouter(
    prefix="/api/v1/prompts",
    tags=['Prompts'],
    dependencies=[Depends(Authenticate)],
)


@router.post("/prompts/", response_model=PromptRead)
def create_prompt(prompt: PromptCreate, db: Session = Depends(get_db)):
  db_prompt = Prompt(name=prompt.name, prompt=prompt.prompt)
  db.add(db_prompt)
  db.commit()
  db.refresh(db_prompt)
  return db_prompt


@router.get("", response_model=List[PromptRead])
def read_prompts(skip: int = 0,
                 limit: int = 10,
                 db: Session = Depends(get_db)):
  prompts = db.query(Prompt).offset(skip).limit(limit).all()
  return prompts



@router.get("/{prompt_id}", response_model=PromptRead)
def read_prompt(prompt_id: int, db: Session = Depends(get_db)):
  prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
  if prompt is None:
    raise HTTPException(status_code=404, detail="Prompt not found")
  return prompt



@router.put("/{prompt_id}", response_model=PromptRead)
def update_prompt(prompt_id: int,
                  prompt: PromptUpdate,
                  db: Session = Depends(get_db)):
  db_prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
  if db_prompt is None:
    raise HTTPException(status_code=404, detail="Prompt not found")

  print("prompt.name",prompt.name)  


  update_data = prompt.model_dump(exclude_unset=True)


  print("update_data",update_data)
  for key, value in update_data.items():
    setattr(db_prompt, key, value)

  db.commit()
  db.refresh(db_prompt)
  return db_prompt



@router.delete("/{prompt_id}", response_model=PromptRead)
def delete_prompt(prompt_id: int, db: Session = Depends(get_db)):
  db_prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
  if db_prompt is None:
    raise HTTPException(status_code=404, detail="Prompt not found")
  db.delete(db_prompt)
  db.commit()
  return db_prompt
