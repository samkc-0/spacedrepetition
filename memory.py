from datetime import datetime, timedelta, timezone
from models import Memory


def tomorrow(memory: Memory, user_answered_correctly: bool) -> Memory:
    if user_answered_correctly:
        updated_memory = memory.model_copy()
        updated_memory.due_date += timedelta(days=1)
        return updated_memory
    return memory


srs_algorithm = tomorrow
