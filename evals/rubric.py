"""
Scoring rubric for evaluating the shopping list parser.
Each function returns (score, max_score, details).
"""


def score_language_detection(result: dict, expected: dict) -> tuple[float, float, str]:
    """Did we detect the right language?"""
    actual = result.get("detected_language", "")
    expected_lang = expected.get("language", "en")
    if actual == expected_lang:
        return 1.0, 1.0, f"✅ Correct: {actual}"
    return 0.0, 1.0, f"❌ Expected {expected_lang}, got {actual}"


def score_item_count(result: dict, expected: dict) -> tuple[float, float, str]:
    """Did we extract at least the minimum expected number of items?"""
    actual = len(result.get("shopping_items", []))
    minimum = expected.get("item_count_min", 0)
    if actual >= minimum:
        return 1.0, 1.0, f"✅ Got {actual} items (min {minimum})"
    return 0.0, 1.0, f"❌ Got {actual} items, expected at least {minimum}"


def score_categories(result: dict, expected: dict) -> tuple[float, float, str]:
    """Did the extracted categories include the expected ones?"""
    expected_cats = set(expected.get("expected_categories", []))
    if not expected_cats:
        return 1.0, 1.0, "✅ No specific categories expected"

    actual_cats = set(item.get("category", "") for item in result.get("shopping_items", []))
    matched = expected_cats & actual_cats
    score = len(matched) / len(expected_cats) if expected_cats else 1.0
    missing = expected_cats - actual_cats
    if score == 1.0:
        return 1.0, 1.0, f"✅ All categories matched: {matched}"
    return score, 1.0, f"⚠️ Matched {matched}, missing {missing}"


def score_calendar(result: dict, expected: dict) -> tuple[float, float, str]:
    """Did we detect calendar events when expected?"""
    has_events = len(result.get("calendar_events", [])) > 0
    expected_events = expected.get("has_calendar_event", False)
    if has_events == expected_events:
        return 1.0, 1.0, f"✅ Calendar events: {'found' if has_events else 'none'} (correct)"
    return 0.0, 1.0, f"❌ Calendar events: {'found' if has_events else 'none'}, expected {'yes' if expected_events else 'none'}"


def score_out_of_scope(result: dict, expected: dict) -> tuple[float, float, str]:
    """Did we correctly identify out-of-scope messages?"""
    actual = result.get("is_out_of_scope", False)
    expected_oos = expected.get("is_out_of_scope", False)
    if actual == expected_oos:
        return 1.0, 1.0, f"✅ Out-of-scope: {actual} (correct)"
    return 0.0, 1.0, f"❌ Out-of-scope: {actual}, expected {expected_oos}"


def score_uncertainty(result: dict, expected: dict) -> tuple[float, float, str]:
    """Did we express uncertainty when we should have?"""
    should_uncertain = expected.get("should_have_uncertainty", False)
    if not should_uncertain:
        return 1.0, 1.0, "✅ No uncertainty expected"

    has_uncertainty = (
        len(result.get("uncertainty_notes", [])) > 0
        or any(item.get("uncertainty_reason") for item in result.get("shopping_items", []))
        or result.get("overall_confidence", 1.0) < 0.6
        or result.get("is_out_of_scope", False)
    )
    if has_uncertainty:
        return 1.0, 1.0, "✅ Uncertainty expressed correctly"
    return 0.0, 1.0, "❌ Should have expressed uncertainty but didn't"


def score_schema_validity(result: dict) -> tuple[float, float, str]:
    """Is the response structurally valid (required fields present, no empty strings where they shouldn't be)?"""
    required = ["detected_language", "original_message", "summary", "shopping_items",
                "calendar_events", "overall_confidence", "is_out_of_scope"]
    missing = [f for f in required if f not in result]
    if missing:
        return 0.0, 1.0, f"❌ Missing fields: {missing}"

    # Check no empty-string item names
    for item in result.get("shopping_items", []):
        if not item.get("item_name", "").strip():
            return 0.0, 1.0, "❌ Empty item_name found"
        if not item.get("search_query", "").strip():
            return 0.0, 1.0, "❌ Empty search_query found"

    return 1.0, 1.0, "✅ Schema is valid"


def score_test_case(result: dict, expected: dict) -> dict:
    """Run all scoring functions and return aggregated results."""
    scores = {}
    scorers = [
        ("language", score_language_detection),
        ("item_count", score_item_count),
        ("categories", score_categories),
        ("calendar", score_calendar),
        ("out_of_scope", score_out_of_scope),
        ("uncertainty", score_uncertainty),
    ]

    total_score = 0.0
    total_max = 0.0

    for name, fn in scorers:
        s, m, detail = fn(result, expected)
        scores[name] = {"score": s, "max": m, "detail": detail}
        total_score += s
        total_max += m

    # Schema validity (no expected needed)
    s, m, detail = score_schema_validity(result)
    scores["schema"] = {"score": s, "max": m, "detail": detail}
    total_score += s
    total_max += m

    scores["total"] = {"score": total_score, "max": total_max,
                        "percentage": round(total_score / total_max * 100, 1) if total_max > 0 else 0}
    return scores
