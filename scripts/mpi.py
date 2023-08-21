import logging
import sys
from pathlib import Path

import click
import lightning as L
import split_learning
import torch
from mpi4py import MPI
from split_learning.models.vision.cnn_2d import CNN2DClient, CNN2DServer
from split_learning.schemas.message import MessageType, WSMessage
from split_learning.utils import datasets as datasets
from split_learning.utils.serde import (
    decode_message_b64,
    deserialize_tensor,
    encode_message_b64,
    serialize_tensor,
)
from torch import nn
from torch.utils.data import DataLoader
from torchvision import transforms
from tqdm import tqdm

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
@click.option("--num-epochs", "num_epochs", type=int, default=50)
@click.option("--batch-size", "batch_size", type=int, default=128)
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
    num_epochs: int,
    batch_size: int,
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

    # interconnect
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    sever_id = 0
    num_clients = comm.Get_size()
    is_sever = rank == sever_id

    if is_sever:
        active_client = 1

        # model
        model = CNN2DServer(in_channels=1, dim_out=10, img_size=28)
        optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=0.9)
        criterion = nn.CrossEntropyLoss()
        model, optimizer = fabric.setup(model, optimizer)

        try:
            while True:
                model.train()
                optimizer.zero_grad()

                messages_bytes = comm.recv(source=active_client)
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
                    comm.send(encoded_response, dest=active_client)
        except Exception as e:
            print(e)
            raise e

    if not is_sever:
        client_id = rank

        # dataset
        mnist_normalize = transforms.Normalize((0.1307,), (0.3081,))
        mnist_train_transform = transforms.Compose(
            [
                transforms.RandomCrop(28, padding=4),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                mnist_normalize,
            ]
        )
        mnist_test_transform = transforms.Compose(
            [
                transforms.ToTensor(),
                mnist_normalize,
            ]
        )
        dataset_mnist_train = datasets.mnist(
            split="train",
            transform=mnist_train_transform,
        )
        dataset_mnist_val = datasets.mnist(
            split="test",
            transform=mnist_test_transform,
        )

        train_loader = DataLoader(
            dataset_mnist_train, batch_size=batch_size, shuffle=True, num_workers=2
        )
        val_loader = DataLoader(
            dataset_mnist_val, batch_size=batch_size, shuffle=True, num_workers=2
        )
        train_loader, val_loader = fabric.setup_dataloaders(train_loader, val_loader)

        # model
        model = CNN2DClient(in_channels=1, dim_out=10, img_size=28)
        optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate, momentum=0.9)
        model, optimizer = fabric.setup(model, optimizer)

        try:
            _logger.info(f"Connecting to {sever_id} ...")

            # start training
            for epoch in range(num_epochs):
                running_loss = 0.0
                pbar = tqdm(enumerate(train_loader))
                for i, data in pbar:
                    images, labels = data["image"], data["label"]

                    model.train()
                    optimizer.zero_grad()

                    activations = model(images)
                    server_inputs = activations.detach().clone()

                    # send smashed activations
                    serialized_inputs = serialize_tensor(server_inputs.cpu())
                    serialized_labels = serialize_tensor(labels.cpu())
                    request_message = WSMessage(
                        type=MessageType.ACTIVATIONS_AND_LABELS,
                        data={"tensor_shape": server_inputs.shape},
                        raw={
                            "tensor": serialized_inputs,
                            "labels": serialized_labels,
                        },
                    )
                    encoded_request = encode_message_b64(request_message)
                    comm.send(encoded_request, dest=sever_id)

                    # receive gradients
                    response_byes = comm.recv(source=sever_id)
                    response = decode_message_b64(response_byes)

                    if response.type == MessageType.GRADS:
                        grads = deserialize_tensor(
                            response.raw["tensor"], dtype=torch.float32
                        )
                        grads = grads.reshape(*response.data["tensor_shape"])
                        grads = grads.to(fabric.device)
                        fabric.backward(activations, grads)
                        optimizer.step()

                        running_loss += response.data["loss"]
                        pbar.set_description(
                            f"[Epoch {epoch}] training loss: {running_loss / (i+1):.4f}"
                        )

                    if i % validate_every == 0:
                        pass

                _logger.info(f"[Epoch {epoch}] train loss: {running_loss}")
        except Exception as e:
            _logger.error(e)
            raise e


if __name__ == "__main__":
    main()
