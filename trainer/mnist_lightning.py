import os

import torch
from dotenv import load_dotenv, find_dotenv
from pytorch_lightning import Trainer
from torch.nn import functional as F
from torch import nn
from pytorch_lightning.core.lightning import LightningModule
from torch.optim import Adam
from torch.utils.data import DataLoader, random_split
from torchvision.datasets import MNIST
from torchvision import datasets, transforms

from trainer.plugins import MinioCheckpointIO
from trainer.callbacks import FederatedCallback


class LitMNIST(LightningModule):
    def __init__(self):
        super().__init__()

        # mnist images are (1, 28, 28) (channels, height, width)
        self.layer_1 = nn.Linear(28 * 28, 128)
        self.layer_2 = nn.Linear(128, 256)
        self.layer_3 = nn.Linear(256, 10)

    def forward(self, x):
        batch_size, channels, height, width = x.size()

        # (b, 1, 28, 28) -> (b, 1*28*28)
        x = x.view(batch_size, -1)
        x = self.layer_1(x)
        x = F.relu(x)
        x = self.layer_2(x)
        x = F.relu(x)
        x = self.layer_3(x)

        x = F.log_softmax(x, dim=1)
        return x

    def training_step(self, batch, batch_idx):
        x, y = batch
        logits = self(x)
        loss = F.nll_loss(logits, y)
        return loss

    def configure_optimizers(self):
        return Adam(self.parameters(), lr=1e-3)

    def train_dataloader(self):
        # transforms
        # prepare transforms standard to MNIST
        transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])
        # data
        mnist_train = MNIST(os.getcwd(), train=True, download=True, transform=transform)
        return DataLoader(mnist_train, batch_size=64)

    # def val_dataloader(self):
    #     transforms = ...
    #     mnist_val = ...
    #     return DataLoader(mnist_val, batch_size=64)
    #
    # def test_dataloader(self):
    #     transforms = ...
    #     mnist_test = ...
    #     return DataLoader(mnist_test, batch_size=64)


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    model = LitMNIST()
    trainer = Trainer(plugins=[MinioCheckpointIO()], callbacks=[FederatedCallback()])
    trainer.fit(model)
