from datetime import datetime
import json
from pathlib import Path
from models import Memory, Sentence, Word


def parse_memory_data(memory_data):
    memory_data["due_date"] = datetime.fromisoformat(
        memory_data["due_date"].replace("Z", "+00:00")
    )
    memory_data["created_at"] = datetime.fromisoformat(
        memory_data["created_at"].replace("Z", "+00:00")
    )
    return Memory(**memory_data)


def parse_word_data(word_data):
    word_data["created_at"] = datetime.fromisoformat(
        word_data["created_at"].replace("Z", "+00:00")
    )
    return Word(**word_data)


def parse_sentence_data(sentence_data):
    sentence_data["created_at"] = datetime.fromisoformat(
        sentence_data["created_at"].replace("Z", "+00:00")
    )
    return Sentence(**sentence_data)


def load_json(name: str, parser):
    with open(Path(".", "data", f"{name}.json")) as f:
        data = [parser(x) for x in json.load(f)]
        assert data[0] is not None
        return data


def seed_test_data() -> dict[str, list]:
    memories = load_json("fake_memories", parse_memory_data)
    words = load_json("words", parse_word_data)
    sentences = load_json("sentences", parse_sentence_data)
    return {"memories": memories, "words": words, "sentences": sentences}
