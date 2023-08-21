from typing import Tuple

from torch import nn
from torchvision import models


class ResNet18Client(nn.Module):
    def __init__(
        self,
        cut_layer: int,
        conv1_swap: bool = False,
        model: nn.Module = None,
        **kwargs,
    ):
        super().__init__()

        self.cut_layer = cut_layer

        self.model = model if model is not None else models.resnet18(pretrained=False)
        if conv1_swap:
            self.model.conv1 = self.conv1 = nn.Conv2d(
                3, 64, kernel_size=3, stride=1, padding=1, bias=False
            )
            self.model.maxpool = nn.Identity()

        children = list(self.model.children())[: cut_layer + 1]
        self.model = nn.Sequential(*children)

    def forward(self, x):
        return self.model(x)


class ResNet18Server(nn.Module):
    def __init__(
        self,
        cut_layer: int,
        num_classes: int,
        model: nn.Module = None,
        **kwargs,
    ):
        super().__init__()

        self.cut_layer = cut_layer

        self.model = model if model is not None else models.resnet18(pretrained=False)
        if self.model.fc.out_features != num_classes:
            num_ftrs = self.model.fc.in_features
            self.model.fc = nn.Sequential(
                nn.Flatten(), nn.Linear(num_ftrs, num_classes)
            )

        children = list(self.model.children())[cut_layer + 1 :]
        self.model = nn.Sequential(*children)

    def forward(self, x):
        return self.model(x)


# U-shape


class ResNet18FrontClient(nn.Module):
    def __init__(
        self,
        cut_layer: Tuple[int],
        conv1_swap: bool = False,
        model: nn.Module = None,
        **kwargs,
    ):
        super().__init__()

        self.cut_layer = cut_layer[0]

        self.model = model if model is not None else models.resnet18(pretrained=False)
        if conv1_swap:
            self.model.conv1 = self.conv1 = nn.Conv2d(
                3, 64, kernel_size=3, stride=1, padding=1, bias=False
            )
            self.model.maxpool = nn.Identity()

        children = list(self.model.children())[: cut_layer + 1]
        self.model = nn.Sequential(*children)

    def forward(self, x):
        return self.model(x)


class ResNet18BackClient(nn.Module):
    def __init__(
        self,
        cut_layer: Tuple[int],
        num_classes: int,
        model: nn.Module = None,
        **kwargs,
    ):
        super().__init__()

        self.cut_layer = cut_layer[1]

        self.model = model if model is not None else models.resnet18(pretrained=False)
        if self.model.fc.out_features != num_classes:
            num_ftrs = self.model.fc.in_features
            self.model.fc = nn.Sequential(
                nn.Flatten(), nn.Linear(num_ftrs, num_classes)
            )

        children = list(self.model.children())[cut_layer + 1 :]
        self.model = nn.Sequential(*children)

    def forward(self, x):
        return self.model(x)


class ResNet18UServer(nn.Module):
    def __init__(
        self,
        cut_layer: Tuple[int],
        model: nn.Module = None,
        **kwargs,
    ):
        super().__init__()

        self.cut_layer = cut_layer

        self.model = model if model is not None else models.resnet18(pretrained=False)
        children = list(self.model.children())[cut_layer[0] + 1 : cut_layer[1] + 1]
        self.model = nn.Sequential(*children)

    def forward(self, x):
        for i, l in enumerate(self.model):
            if i <= self.cut_layer[0]:
                continue
            elif i > self.cut_layer[1]:
                break
            x = l(x)
        return nn.functional.softmax(x, dim=1)
