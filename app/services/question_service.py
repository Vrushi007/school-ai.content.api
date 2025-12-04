from sqlalchemy.orm import Session
from app.models.question import Question
from app.schemas.question import QuestionCreate, QuestionUpdate, QuestionBulkCreate
from typing import List


def create_question(db: Session, question: QuestionCreate) -> Question:
    db_question = Question(**question.model_dump())
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question


def create_questions_bulk(db: Session, bulk_data: QuestionBulkCreate) -> List[Question]:
    questions = []
    for q_data in bulk_data.questions:
        q_dict = q_data.model_dump()
        q_dict["chapter_id"] = bulk_data.chapter_id
        db_question = Question(**q_dict)
        db.add(db_question)
        questions.append(db_question)
    
    db.commit()
    for q in questions:
        db.refresh(q)
    return questions


def get_questions_by_chapter(db: Session, chapter_id: int) -> List[Question]:
    return db.query(Question).filter(Question.chapter_id == chapter_id).all()


def get_question_by_id(db: Session, question_id: int) -> Question | None:
    return db.query(Question).filter(Question.id == question_id).first()


def update_question(db: Session, question_id: int, question_update: QuestionUpdate) -> Question | None:
    db_question = get_question_by_id(db, question_id)
    if not db_question:
        return None
    
    update_data = question_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_question, field, value)
    
    db.commit()
    db.refresh(db_question)
    return db_question


def delete_question(db: Session, question_id: int) -> bool:
    db_question = get_question_by_id(db, question_id)
    if not db_question:
        return False
    
    db.delete(db_question)
    db.commit()
    return True

