import torch
import torch.nn as nn


# Model (simple CNN adapted from 'PyTorch: A 60 Minute Blitz')
# Follows closely to LeNet-5 architecture
class CNN2D(nn.Module):
    def __init__(self, in_channels=3, dim_out=10, img_size=32) -> None:
        super().__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(
                in_channels=in_channels, out_channels=6, kernel_size=5, padding=2
            ),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(in_channels=6, out_channels=16, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )
        self.fc = nn.Sequential(
            nn.Linear(16 * (img_size // 4) ** 2, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, dim_out),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv1(x)
        x = self.conv2(x)
        x = x.flatten(1)
        return self.fc(x)


class CNN2DClient(nn.Module):
    def __init__(self, in_channels=3, dim_out=10, img_size=32):
        super().__init__()

        self.model = CNN2D(in_channels, dim_out, img_size)

    def forward(self, x):
        return self.model.conv1(x)


class CNN2DServer(nn.Module):
    def __init__(self, in_channels=3, dim_out=10, img_size=32):
        super().__init__()

        self.model = CNN2D(in_channels, dim_out, img_size)

    def forward(self, x: torch.Tensor):
        x = self.model.conv2(x)
        x = x.flatten(1)
        x = self.model.fc(x)
        return x
