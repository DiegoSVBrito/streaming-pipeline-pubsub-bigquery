import json
import logging
from datetime import datetime
from schema import EventMessage


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )


def parse_message(raw: dict) -> dict:
    try:
        data = EventMessage(**raw)
        data.processed_at = datetime.utcnow()
        return {"valid": True, "data": data}
    except Exception as e:
        return {"valid": False, "error": str(e), "raw": raw}
