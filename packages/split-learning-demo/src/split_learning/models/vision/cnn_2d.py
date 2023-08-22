import torch
import torch.nn as nn


# Model (simple CNN adapted from 'PyTorch: A 60 Minute Blitz')
# Follows closely to LeNet-5 architecture
class CNN2D(nn.Module):
    def __init__(
        self,
        in_channels=3,
        dim_out=10,
        img_size=32,
        activation="ReLU",
        norm=None,
        linear_norm=None,
        dropout=0.4,
    ) -> None:
        super().__init__()

        self.activation = getattr(nn, activation)
        self.norm = getattr(nn, norm) if norm is not None else nn.Identity
        self.linear_norm = (
            getattr(nn, linear_norm) if linear_norm is not None else nn.Identity
        )
        self.dropout = nn.Dropout if dropout is not None else nn.Identity

        self.conv1 = nn.Sequential(
            nn.Conv2d(
                in_channels=in_channels, out_channels=6, kernel_size=5, padding=2
            ),
            self.norm(6),
            self.activation(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            self.dropout(dropout),
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(in_channels=6, out_channels=16, kernel_size=5, padding=2),
            self.norm(16),
            self.activation(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            self.dropout(dropout),
        )

        features_in = 16 * (img_size // 4) ** 2
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(features_in, 256),
            self.linear_norm(256),
            self.activation(),
            nn.Linear(256, 128),
            self.linear_norm(128),
            self.activation(),
            self.dropout(dropout),
            nn.Linear(128, dim_out),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv1(x)
        x = self.conv2(x)
        return self.fc(x)


class CNN2DClient(nn.Module):
    def __init__(
        self,
        model: nn.Module = None,
        **kwargs,
    ):
        super().__init__()

        self.cut_layer = 1

        self.model = model if model is not None else CNN2D(**kwargs)
        children = list(self.model.children())[: self.cut_layer + 1]
        self.model = nn.Sequential(*children)

    def forward(self, x):
        return self.model(x)


class CNN2DServer(nn.Module):
    def __init__(
        self,
        model: nn.Module = None,
        **kwargs,
    ):
        super().__init__()

        self.cut_layer = 1

        self.model = model if model is not None else CNN2D(**kwargs)
        children = list(self.model.children())[self.cut_layer + 1 :]
        self.model = nn.Sequential(*children)

    def forward(self, x: torch.Tensor):
        return self.model(x)
