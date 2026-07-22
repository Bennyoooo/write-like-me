from write_like_me.analyze import analyze, context_markdown, profile_markdown


def test_analysis_extracts_voice_traits() -> None:
    profile = analyze([
        "i think this should work. can you test it? i think we should ship it.",
        "i think the smaller version is clearer. can you keep it direct?",
    ])

    assert profile["sample_count"] == 2
    assert profile["question_rate"] > 0
    assert profile["lowercase_sentence_rate"] > 0
    assert "i think" in profile["recurring_phrases"]
    assert "Writing instructions" in profile_markdown(profile)


def test_empty_profile_has_helpful_message() -> None:
    assert "No writing samples" in profile_markdown(analyze([]))


def test_context_includes_bounded_reference_excerpts() -> None:
    sample = "This is how I tend to explain a decision clearly and directly."
    context = context_markdown(analyze([sample]), [sample])
    assert "Reference excerpts" in context
    assert sample in context
    assert "style evidence" in context
