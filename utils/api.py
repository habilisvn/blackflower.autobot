from dataclasses import dataclass


@dataclass
class BodyData:
    message: str


@dataclass
class APIBody:
    # Session ID is used to identify the session
    # A session can be persisted (in some cases - developing feature)
    session_id: str
    ai_agent: str
    data: BodyData
