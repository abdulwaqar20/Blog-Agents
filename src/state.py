from typing import TypedDict

class State(TypedDict):
    topic: str
    outline: str
    draft: str
    feedback: str
    retries: int
    approved: bool