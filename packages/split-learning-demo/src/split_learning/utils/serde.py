import base64
import json
from typing import Type, TypeVar

import numpy as np
import torch
from bitarray import bitarray
from bitarray.util import ba2int, int2ba
from pydantic import BaseModel
from split_learning.schemas.message import WSMessage

# dtypes

numpy_to_torch_dtype_dict = {
    np.uint8: torch.uint8,
    np.int8: torch.int8,
    np.int16: torch.int16,
    np.int32: torch.int32,
    np.int64: torch.int64,
    np.float16: torch.float16,
    np.float32: torch.float32,
    np.float64: torch.float64,
    np.complex64: torch.complex64,
    np.complex128: torch.complex128,
}
torch_to_numpy_dtype_dict = {
    value: key for (key, value) in numpy_to_torch_dtype_dict.items()
}


# tensors


def serialize_tensor(tensors: torch.Tensor):
    return serialize_numpy(tensors.numpy())


def serialize_numpy(tensors: np.ndarray):
    return np.ascontiguousarray(tensors).tobytes()


def deserialize_tensor(data: bytes, squeeze=True, dtype=torch.float32):
    if dtype not in numpy_to_torch_dtype_dict.values():
        raise ValueError(f"Invalid dtype: {dtype}")

    numpy_dtype = torch_to_numpy_dtype_dict[dtype]
    numpy_tensor = deserialize_numpy(data, squeeze=squeeze, dtype=numpy_dtype)
    return torch.from_numpy(numpy_tensor.copy())


def deserialize_numpy(data: bytes, squeeze=True, dtype=np.float32):
    if dtype not in numpy_to_torch_dtype_dict.keys():
        raise ValueError(f"Invalid dtype: {dtype}")

    arr = np.frombuffer(data, dtype=dtype)
    if squeeze:
        arr = np.squeeze(arr)

    return arr


# pydantic


T = TypeVar("T")


def encode_message_b64(message: BaseModel) -> bytes:
    json_string = message.json()
    json_bytes = json_string.encode("utf-8")
    base64_bytes = base64.b64encode(json_bytes)

    return base64_bytes


def decode_message_b64(data: bytes, schema: Type[T] = WSMessage) -> T:
    decoded_bytes = base64.b64decode(data)
    decoded_string = decoded_bytes.decode("utf-8")
    message_dict = json.loads(decoded_string)
    message = schema(**message_dict)

    return message
