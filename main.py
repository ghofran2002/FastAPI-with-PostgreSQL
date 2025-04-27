from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated

import model
from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

# Crée les tables
model.Base.metadata.create_all(bind=engine)

# Pydantic Models
class ChoiceBase(BaseModel):
    choice_text: str
    is_correct: bool

class QuestionBase(BaseModel):
    question_text: str
    choices: List[ChoiceBase]

# Connection BDD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency
db_dependency = Annotated[Session, Depends(get_db)]

# Endpoint POST pour créer une question
@app.post('/questions/')
def create_questions(question: QuestionBase, db: db_dependency):
    db_question = model.Questions(question_text=question.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    for choice in question.choices:
        db_choice = model.Choices(choice_text=choice.choice_text, is_correct=choice.is_correct, question_id=db_question.id)
        db.add(db_choice)
    db.commit()
    return {"message": "Question and choices created successfully"}

# Endpoint GET pour récupérer une question
@app.get('/questions/{question_id}')
def read_questions(question_id: int, db: db_dependency):
    result = db.query(model.Questions).filter(model.Questions.id == question_id).first()
    if not result:
        raise HTTPException(status_code=404, detail='Question not found')
    return result

# Endpoint GET pour récupérer les choix d'une question
@app.get('/choices/{question_id}')
def read_choices(question_id: int, db: db_dependency):
    result = db.query(model.Choices).filter(model.Choices.question_id == question_id).all()
    if not result:
        raise HTTPException(status_code=404, detail='Choices not found')
    return result
