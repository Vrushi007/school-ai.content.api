import hashlib
from typing import Optional


def generate_input_hash(
    board_id: int,
    class_id: int,
    subject_id: int,
    chapter_id: int,
    planned_sessions: int,
    user_id: Optional[int] = None
) -> str:
    """
    Generate a SHA-256 hex digest for a normalized input string.

    Normalized format:
    "{user_id}|{board_id}|{class_id}|{subject_id}|{chapter_id}|{planned_sessions}"
    
    Note: user_id is optional for backward compatibility with legacy data.
    """
    normalized = f"{user_id}|{board_id}|{class_id}|{subject_id}|{chapter_id}|{planned_sessions}"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
