from typing import Any, Optional

from pytorch_lightning.callbacks import Callback
from pytorch_lightning.utilities.types import STEP_OUTPUT
import pytorch_lightning as pl


class FederatedCallback(Callback):

    def __init__(self) -> None:
        super().__init__()

    def on_train_batch_end(self, trainer: "pl.Trainer", pl_module: "pl.LightningModule", outputs: STEP_OUTPUT,
                           batch: Any, batch_idx: int, unused: Optional[int] = 0) -> None:
        print("FederatedCallback: on_train_batch_end")
        super().on_train_batch_end(trainer, pl_module, outputs, batch, batch_idx, unused)
