from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.key_point import KeyPointCreate, KeyPointResponse, KeyPointUpdate
from app.services import key_point_service

router = APIRouter(
    prefix="/key-points",
    tags=["Key Points"]
)


@router.post("/", response_model=List[KeyPointResponse], status_code=status.HTTP_201_CREATED)
async def create_key_point(
    key_points: List[KeyPointCreate],
    db: Session = Depends(get_db)
):
    """Create one or more key points (with associated content records)"""
    # Check if any codes already exist
    for key_point in key_points:
        existing = key_point_service.get_key_point_by_code(db, key_point.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Key point with code '{key_point.code}' already exists"
            )
    
    return key_point_service.create_key_point(db, key_points)


@router.get("/{key_point_id}", response_model=KeyPointResponse)
async def get_key_point(
    key_point_id: int,
    db: Session = Depends(get_db)
):
    """Get a key point by ID"""
    key_point = key_point_service.get_key_point_by_id(db, key_point_id)
    if not key_point:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Key point not found"
        )
    return key_point


@router.get("/", response_model=List[KeyPointResponse])
async def get_key_points(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all key points with pagination"""
    return key_point_service.get_all_key_points(db, skip=skip, limit=limit)


@router.get("/chapter/{chapter_id}", response_model=List[KeyPointResponse])
async def get_key_points_by_chapter(
    chapter_id: int,
    db: Session = Depends(get_db)
):
    """Get all key points for a specific chapter"""
    return key_point_service.get_key_points_by_chapter(db, chapter_id)


@router.put("/{key_point_id}", response_model=KeyPointResponse)
async def update_key_point(
    key_point_id: int,
    key_point_update: KeyPointUpdate,
    db: Session = Depends(get_db)
):
    """Update a key point"""
    key_point = key_point_service.update_key_point(db, key_point_id, key_point_update)
    if not key_point:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Key point not found"
        )
    return key_point


@router.delete("/{key_point_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_key_point(
    key_point_id: int,
    db: Session = Depends(get_db)
):
    """Delete a key point"""
    success = key_point_service.delete_key_point(db, key_point_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Key point not found"
        )
    return None

