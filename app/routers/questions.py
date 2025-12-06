from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.question import QuestionCreate, QuestionResponse, QuestionUpdate, QuestionBulkCreate
from app.services import question_service, chapter_service

router = APIRouter(prefix="/questions", tags=["questions"])


@router.post("", response_model=QuestionResponse, status_code=201)
async def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    # Validate chapter exists
    chapter = chapter_service.get_chapter_by_id(db, question.chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    return question_service.create_question(db, question)


@router.post("/bulk", response_model=List[QuestionResponse], status_code=201)
async def create_questions_bulk(bulk_data: QuestionBulkCreate, db: Session = Depends(get_db)):
    # Validate chapter exists
    chapter = chapter_service.get_chapter_by_id(db, bulk_data.chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    return question_service.create_questions_bulk(db, bulk_data)


@router.get("/chapters/{chapter_id}", response_model=List[QuestionResponse])
async def get_questions_by_chapter(chapter_id: int, db: Session = Depends(get_db)):
    return question_service.get_questions_by_chapter(db, chapter_id)


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(question_id: int, db: Session = Depends(get_db)):
    question = question_service.get_question_by_id(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(question_id: int, question_update: QuestionUpdate, db: Session = Depends(get_db)):
    if question_update.chapter_id:
        chapter = chapter_service.get_chapter_by_id(db, question_update.chapter_id)
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")
    
    updated = question_service.update_question(db, question_id, question_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Question not found")
    return updated


@router.delete("/{question_id}", status_code=204)
async def delete_question(question_id: int, db: Session = Depends(get_db)):
    success = question_service.delete_question(db, question_id)
    if not success:
        raise HTTPException(status_code=404, detail="Question not found")
    return None

