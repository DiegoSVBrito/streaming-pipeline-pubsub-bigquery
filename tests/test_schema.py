import pytest
from datetime import datetime, timezone
from schema import EventMessage


def test_valid_message():
    msg = EventMessage(
        event_id="abc123",
        event_type="click",
        source="web",
        event_timestamp=datetime.now(timezone.utc),
    )
    assert msg.event_id == "abc123"
    assert msg.source == "web"


def test_invalid_event_type():
    with pytest.raises(ValueError):
        EventMessage(
            event_id="abc123",
            event_type="invalid_type",
            event_timestamp=datetime.now(timezone.utc),
        )


def test_missing_required_field():
    with pytest.raises(ValueError):
        EventMessage(event_type="click")


def test_default_source():
    msg = EventMessage(
        event_id="abc123",
        event_type="click",
        event_timestamp=datetime.now(timezone.utc),
    )
    assert msg.source == "unknown"


def test_optional_payload():
    msg = EventMessage(
        event_id="abc123",
        event_type="purchase",
        payload={"amount": 99.90},
        event_timestamp=datetime.now(timezone.utc),
    )
    assert msg.payload["amount"] == 99.90
