import base64
from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel, validator


# enum
class MessageType(str, Enum):
    ACTIVATIONS = "activations"
    ACTIVATIONS_AND_LABELS = "activations_and_labels"
    GRADS = "grads"
    LABELS = "labels"


class WSMessage(BaseModel):
    type: MessageType
    data: Dict[str, Any] = {}
    raw: Dict[str, bytes] = {}

    class Config:
        json_encoders = {bytes: lambda x: base64.b64encode(x).decode("utf-8")}

    @validator("raw", pre=True)
    def decode_base64(cls, value: Dict[str, str]) -> Dict[str, bytes]:
        return {
            k: (base64.b64decode(v) if isinstance(v, str) else v)
            for k, v in value.items()
        }
