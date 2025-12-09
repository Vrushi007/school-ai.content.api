from app.schemas.board import BoardCreate, BoardResponse, BoardUpdate
from app.schemas.state import StateCreate, StateResponse
from app.schemas.syllabus import SyllabusCreate, SyllabusResponse, SyllabusUpdate
from app.schemas.class_model import ClassCreate, ClassResponse, ClassUpdate
from app.schemas.subject import SubjectCreate, SubjectResponse, SubjectUpdate
from app.schemas.chapter import ChapterCreate, ChapterResponse, ChapterUpdate
from app.schemas.key_point import KeyPointCreate, KeyPointResponse, KeyPointUpdate, KeyPointBulkCreate
from app.schemas.question import QuestionCreate, QuestionResponse, QuestionUpdate, QuestionBulkCreate
from app.schemas.answer import AnswerCreate, AnswerResponse
from app.schemas.lesson_plan import LessonPlanGenerateRequest, LessonPlanGenerateResponse

__all__ = [
    "BoardCreate",
    "BoardResponse",
    "BoardUpdate",
    "StateCreate",
    "StateResponse",
    "SyllabusCreate",
    "SyllabusResponse",
    "SyllabusUpdate",
    "ClassCreate",
    "ClassResponse",
    "ClassUpdate",
    "SubjectCreate",
    "SubjectResponse",
    "SubjectUpdate",
    "ChapterCreate",
    "ChapterResponse",
    "ChapterUpdate",
    "KeyPointCreate",
    "KeyPointResponse",
    "KeyPointUpdate",
    "KeyPointBulkCreate",
    "QuestionCreate",
    "QuestionResponse",
    "QuestionUpdate",
    "QuestionBulkCreate",
    "AnswerCreate",
    "AnswerResponse",
    "LessonPlanGenerateRequest",
    "LessonPlanGenerateResponse",
]

