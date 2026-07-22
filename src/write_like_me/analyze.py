from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any


WORD = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)?")
SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from", "had", "has",
    "have", "he", "her", "his", "i", "in", "is", "it", "its", "me", "my", "of", "on",
    "or", "our", "she", "so", "that", "the", "their", "them", "they", "this", "to", "was",
    "we", "were", "will", "with", "you", "your",
}


def _round(value: float) -> float:
    return round(value, 2)


def _ratio(numerator: int, denominator: int) -> float:
    return _round(numerator / denominator) if denominator else 0.0


def analyze(texts: list[str]) -> dict[str, Any]:
    joined = "\n\n".join(texts)
    words = WORD.findall(joined)
    lowered = [word.lower().replace("’", "'") for word in words]
    sentences = [part.strip() for part in SENTENCE.split(joined) if WORD.search(part)]
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", joined) if WORD.search(part)]
    meaningful = [word for word in lowered if word not in STOP_WORDS and len(word) > 2]
    ngrams: Counter[str] = Counter()
    for size in (2, 3):
        for index in range(len(lowered) - size + 1):
            phrase_words = lowered[index:index + size]
            if not all(word in STOP_WORDS for word in phrase_words):
                ngrams[" ".join(phrase_words)] += 1
    openers = Counter()
    for sentence in sentences:
        sentence_words = [word.lower() for word in WORD.findall(sentence)[:3]]
        if sentence_words:
            openers[" ".join(sentence_words)] += 1
    punctuation = Counter(char for char in joined if char in ".,!?;:()—-")
    contractions = sum("'" in word or "’" in word for word in words)
    list_lines = sum(bool(re.match(r"\s*(?:[-*]|\d+[.)])\s+", line)) for line in joined.splitlines())
    lowercase_starts = sum(bool(re.match(r"[a-z]", sentence)) for sentence in sentences)
    emoji = len(re.findall(r"[^\x00-\x7F]", joined))
    return {
        "sample_count": len(texts),
        "word_count": len(words),
        "sentence_count": len(sentences),
        "paragraph_count": len(paragraphs),
        "avg_words_per_sentence": _round(len(words) / max(len(sentences), 1)),
        "avg_sentences_per_paragraph": _round(len(sentences) / max(len(paragraphs), 1)),
        "avg_word_length": _round(sum(map(len, words)) / max(len(words), 1)),
        "vocabulary_diversity": _round(len(set(lowered)) / max(len(lowered), 1)),
        "contraction_rate": _ratio(contractions, len(words)),
        "question_rate": _ratio(joined.count("?"), len(sentences)),
        "exclamation_rate": _ratio(joined.count("!"), len(sentences)),
        "lowercase_sentence_rate": _ratio(lowercase_starts, len(sentences)),
        "list_line_rate": _ratio(list_lines, max(len(joined.splitlines()), 1)),
        "emoji_per_1000_words": _round(emoji * 1000 / max(len(words), 1)),
        "first_person_rate": _ratio(sum(word in {"i", "me", "my", "we", "us", "our"} for word in lowered), len(words)),
        "second_person_rate": _ratio(sum(word in {"you", "your", "yours"} for word in lowered), len(words)),
        "favorite_words": [word for word, _ in Counter(meaningful).most_common(12)],
        "recurring_phrases": [phrase for phrase, count in ngrams.most_common(12) if count >= 2],
        "common_openers": [phrase for phrase, count in openers.most_common(8) if count >= 2],
        "punctuation": dict(punctuation.most_common()),
        "confidence": _round(min(1.0, math.log1p(len(words)) / math.log(1501))),
    }


def profile_markdown(profile: dict[str, Any]) -> str:
    if profile["sample_count"] == 0:
        return "No writing samples yet. Keep capture enabled or run `wlm capture`."
    confidence = profile["confidence"]
    evidence = "low" if confidence < 0.45 else "medium" if confidence < 0.75 else "high"
    traits: list[str] = []
    sentence_length = profile["avg_words_per_sentence"]
    traits.append("short, direct sentences" if sentence_length < 12 else "long, developed sentences" if sentence_length > 22 else "medium-length sentences")
    traits.append("frequent questions" if profile["question_rate"] > 0.18 else "questions used sparingly")
    traits.append("frequent contractions" if profile["contraction_rate"] > 0.025 else "mostly uncontracted wording")
    traits.append("list-driven structure" if profile["list_line_rate"] > 0.18 else "mostly prose structure")
    if profile["lowercase_sentence_rate"] > 0.2:
        traits.append("intentional lowercase sentence openings")
    if profile["exclamation_rate"] > 0.12:
        traits.append("expressive exclamation marks")
    lines = [
        "# Writing Voice Profile",
        "",
        f"Evidence: {profile['sample_count']} samples, {profile['word_count']} words ({evidence} confidence).",
        "",
        "## Observed tendencies",
        "",
        *(f"- {trait}" for trait in traits),
        f"- Average sentence length: {profile['avg_words_per_sentence']} words",
        f"- Average paragraph depth: {profile['avg_sentences_per_paragraph']} sentences",
    ]
    if profile["favorite_words"]:
        lines.extend(["- Characteristic vocabulary: " + ", ".join(profile["favorite_words"][:8])])
    if profile["recurring_phrases"]:
        lines.extend(["- Recurring phrases: " + ", ".join(profile["recurring_phrases"][:6])])
    lines.extend([
        "",
        "## Writing instructions",
        "",
        "Write in the user's voice while preserving the requested meaning and factual accuracy.",
        f"Aim for about {max(5, round(profile['avg_words_per_sentence']))} words per sentence on average, but vary the rhythm naturally.",
        "Match the observed capitalization, paragraph density, contraction use, and punctuation without exaggerating them.",
        "Prefer the user's recurring vocabulary only when it fits. Do not copy errors, secrets, or topic-specific details from examples.",
        "Do not mention this profile or claim to be the user.",
    ])
    return "\n".join(lines) + "\n"

