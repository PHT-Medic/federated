from typing import Any, Optional, Dict

from pytorch_lightning.callbacks import Callback, EarlyStopping
from pytorch_lightning.utilities.types import STEP_OUTPUT
import pytorch_lightning as pl


class FederatedCallback(Callback):

    def __init__(self) -> None:
        super().__init__()

    def on_train_batch_end(self, trainer: "pl.Trainer", pl_module: "pl.LightningModule", outputs: STEP_OUTPUT,
                           batch: Any, batch_idx: int, unused: Optional[int] = 0) -> None:
        super().on_train_batch_end(trainer, pl_module, outputs, batch, batch_idx, unused)

    def on_save_checkpoint(self, trainer: "pl.Trainer", pl_module: "pl.LightningModule",
                           checkpoint: Dict[str, Any]) -> dict:

        print("on_save_checkpoint")

        checkpoint = super().on_save_checkpoint(trainer, pl_module, checkpoint)

        trainer.should_stop = True

        return checkpoint

    def on_load_checkpoint(self, trainer: "pl.Trainer", pl_module: "pl.LightningModule",
                           callback_state: Dict[str, Any]) -> None:
        super().on_load_checkpoint(trainer, pl_module, callback_state)


