import hashlib


def generate_input_hash(
    board_id: int,
    class_id: int,
    subject_id: int,
    chapter_id: int,
    planned_sessions: int
) -> str:
    """
    Generate a SHA-256 hex digest for a normalized input string.

    Normalized format:
    "{board_id}|{class_id}|{subject_id}|{chapter_id}|{planned_sessions}"
    """
    normalized = f"{board_id}|{class_id}|{subject_id}|{chapter_id}|{planned_sessions}"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
