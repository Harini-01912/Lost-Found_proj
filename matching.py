import re
from difflib import SequenceMatcher

from database import get_db


MATCH_THRESHOLD = 30
FIELD_WEIGHTS = {
    "name": 0.40,
    "category": 0.20,
    "description": 0.25,
    "location": 0.15,
}


def _normalized_text(value):
    return " ".join(re.findall(r"\w+", value.casefold()))


def _text_similarity(first, second):
    first_normalized = _normalized_text(first)
    second_normalized = _normalized_text(second)
    if not first_normalized or not second_normalized:
        return 0.0
    sequence_score = SequenceMatcher(
        None, first_normalized, second_normalized
    ).ratio()
    first_words = set(first_normalized.split())
    second_words = set(second_normalized.split())
    union = first_words | second_words
    word_score = len(first_words & second_words) / len(union) if union else 0.0
    return (sequence_score + word_score) / 2


def match_score(first, second):
    weighted_score = 0.0
    for field, weight in FIELD_WEIGHTS.items():
        if field == "category":
            similarity = float(first[field].casefold() == second[field].casefold())
        else:
            similarity = _text_similarity(first[field], second[field])
        weighted_score += similarity * weight
    return round(weighted_score * 100)


def find_matches(item, opposite_kind):
    rows = get_db().execute(
        "SELECT * FROM items WHERE kind = ? ORDER BY created_at DESC, id DESC",
        (opposite_kind,),
    ).fetchall()
    matches = []
    for candidate in rows:
        score = match_score(item, candidate)
        if score >= MATCH_THRESHOLD:
            matches.append({"item": candidate, "score": score})
    return sorted(matches, key=lambda match: match["score"], reverse=True)
