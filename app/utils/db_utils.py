"""
Database utility functions for idempotent operations.
"""
from sqlalchemy.orm import Session
from typing import Type, TypeVar, Dict, Any, Optional

ModelType = TypeVar('ModelType')


def get_or_create(
    db: Session,
    model: Type[ModelType],
    filters: Dict[str, Any],
    defaults: Optional[Dict[str, Any]] = None
) -> ModelType:
    """
    Get an instance of the model matching the filters, or create it if it doesn't exist.
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        filters: Dictionary of filters to search by (e.g., {"name": "CBSE"})
        defaults: Dictionary of default values to use when creating (merged with filters)
    
    Returns:
        The existing or newly created model instance
    """
    # Try to find existing instance
    instance = db.query(model).filter_by(**filters).first()
    
    if instance:
        # Update with defaults if provided and instance exists
        if defaults:
            for key, value in defaults.items():
                if not hasattr(instance, key) or getattr(instance, key) is None:
                    setattr(instance, key, value)
            db.commit()
            db.refresh(instance)
        return instance
    
    # Create new instance
    params = {**filters}
    if defaults:
        params.update(defaults)
    
    instance = model(**params)
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


def get_or_fail(
    db: Session,
    model: Type[ModelType],
    filters: Dict[str, Any],
    error_message: str
) -> ModelType:
    """
    Get an instance of the model matching the filters, or raise an error if not found.
    
    Args:
        db: Database session
        model: SQLAlchemy model class
        filters: Dictionary of filters to search by
        error_message: Error message to raise if not found
    
    Returns:
        The model instance
    
    Raises:
        ValueError: If instance not found
    """
    instance = db.query(model).filter_by(**filters).first()
    if not instance:
        raise ValueError(error_message)
    return instance

