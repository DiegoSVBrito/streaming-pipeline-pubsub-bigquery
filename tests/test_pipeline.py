from utils import parse_message
from datetime import datetime, timezone


def test_parse_valid_message():
    raw = {
        "event_id": "test-001",
        "event_type": "click",
        "source": "web",
        "event_timestamp": datetime.now(timezone.utc).isoformat(),
    }
    result = parse_message(raw)
    assert result["valid"] is True
    assert result["data"].event_id == "test-001"


def test_parse_invalid_message():
    raw = {"event_id": "", "event_type": "invalid"}
    result = parse_message(raw)
    assert result["valid"] is False
    assert "error" in result


def test_parse_missing_fields():
    raw = {}
    result = parse_message(raw)
    assert result["valid"] is False
