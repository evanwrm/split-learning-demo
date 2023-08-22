import logging
import sys
from pathlib import Path
from typing import Any

import click
import lightning as L
import torch
from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from torch import nn
from uvicorn import Config, Server

import split_learning
from split_learning.models.vision.cnn_2d import CNN2D, CNN2DServer
from split_learning.schemas.message import MessageType, WSMessage
from split_learning.utils import utils
from split_learning.utils.serde import (
    decode_message_b64,
    deserialize_tensor,
    encode_message_b64,
    serialize_tensor,
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send(self, websocket: WebSocket, message: Any):
        await websocket.send(message)

    async def send_bytes(self, websocket: WebSocket, message: bytes):
        await websocket.send_bytes(message)

    async def broadcast(self, message: Any):
        for connection in self.active_connections:
            await connection.send(message)

    async def broadcast_bytes(self, message: bytes):
        for connection in self.active_connections:
            await connection.send_bytes(message)


# logger
_logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "-c",
    "--config",
    "cfg_path",
    type=click.Path(exists=True),
    help="path to config file",
)
# training
@click.option("--learning-rate", "learning_rate", type=float, default=1e-4)
@click.option("--grad-clip", "grad_clip", type=float, default=0.5)
# logging
@click.option("--grad-accumulate-every", "grad_accumulate_every", type=int, default=4)
@click.option("--validate-every", "validate_every", type=int, default=100)
@click.option("--generate-every", "generate_every", type=int, default=500)
# log levels
@click.option("-q", "--quiet", "log_level", flag_value=logging.WARNING)
@click.option("-v", "--verbose", "log_level", flag_value=logging.INFO, default=True)
@click.option("-vv", "--very-verbose", "log_level", flag_value=logging.DEBUG)
# version
@click.version_option(split_learning.__version__)
def main(
    cfg_path: Path,
    # training
    learning_rate: float,
    grad_clip: float,
    # logging
    grad_accumulate_every: int,
    validate_every: int,
    generate_every: int,
    # log levels
    log_level: int,
):
    # logging
    logging.basicConfig(
        stream=sys.stdout,
        level=log_level,
        datefmt="%Y-%m-%d %H:%M",
        format="[%(asctime)s] %(levelname)s: %(message)s",
    )

    # accelerator
    fabric = L.Fabric(accelerator="gpu", precision="32-true")
    fabric.launch()

    # webserver
    api_prefix = "/api/v1"
    app = FastAPI(title="split-learning", openapi_url=f"{api_prefix}/openapi.json")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    manager = ConnectionManager()

    # model
    model = CNN2D(
        in_channels=1,
        dim_out=10,
        img_size=28,
        dropout=0.15,
    )
    model_path = utils.data_path() / "models/mnist/model.pt"
    model.load_state_dict(torch.load(model_path))

    model = CNN2DServer(in_channels=1, dim_out=10, img_size=28, model=model)
    optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=0.9)
    criterion = nn.CrossEntropyLoss()
    model, optimizer = fabric.setup(model, optimizer)

    @app.websocket("/ws", api_prefix)
    async def websocket_endpoint(websocket: WebSocket):
        await manager.connect(websocket)
        try:
            while True:
                optimizer.zero_grad()

                messages_bytes = await websocket.receive_bytes()
                message = decode_message_b64(messages_bytes)

                if message.type == MessageType.ACTIVATIONS_AND_LABELS:
                    activations = deserialize_tensor(
                        message.raw["tensor"], dtype=torch.float32
                    )
                    labels = deserialize_tensor(
                        message.raw["labels"], dtype=torch.int64
                    )

                    activations = activations.to(fabric.device)
                    activations = activations.reshape(*message.data["tensor_shape"])
                    labels = labels.to(fabric.device)

                    model.train()
                    activations.requires_grad = True
                    outputs = model(activations)
                    loss = criterion(outputs, labels)
                    fabric.backward(loss)

                    optimizer.step()

                    # send grads
                    grads = activations.grad
                    client_grads = grads.detach().clone()
                    serialized_grads = serialize_tensor(client_grads.cpu())
                    response_message = WSMessage(
                        type=MessageType.GRADS,
                        data={"tensor_shape": grads.shape, "loss": loss.item()},
                        raw={"tensor": serialized_grads},
                    )
                    encoded_response = encode_message_b64(response_message)
                    await websocket.send_bytes(encoded_response)
                elif message.type == MessageType.ACTIVATIONS:
                    activations = deserialize_tensor(
                        message.raw["tensor"], dtype=torch.float32
                    )

                    activations = activations.to(fabric.device)
                    activations = activations.reshape(*message.data["tensor_shape"])

                    model.eval()
                    outputs = model(activations)

                    # send logits
                    logits = outputs.detach().clone()
                    serialized_logits = serialize_tensor(logits.cpu())
                    response_message = WSMessage(
                        type=MessageType.LOGITS,
                        data={"tensor_shape": logits.shape},
                        raw={"tensor": serialized_logits},
                    )
                    encoded_response = encode_message_b64(response_message)
                    await websocket.send_bytes(encoded_response)
        except WebSocketDisconnect:
            manager.disconnect(websocket)
        except Exception as e:
            _logger.error(e)
            raise e

    server_config = Config(
        app=app, host="127.0.0.1", port=8000, ws_max_size=64 * 1024 * 1024
    )
    server = Server(config=server_config)
    server.run()


if __name__ == "__main__":
    main()
