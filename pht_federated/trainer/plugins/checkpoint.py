import os
import uuid
from io import BytesIO
from typing import Any, Callable, Dict, Optional

import torch
from pytorch_lightning.plugins.io import TorchCheckpointIO
from pytorch_lightning.utilities.types import _PATH
from s3fs import S3FileSystem

from pht_federated.client.storage import MinioBuckets, get_minio_fs


class MinioCheckpointIO(TorchCheckpointIO):
    def __init__(self, minio_fs: S3FileSystem = None, id: str = None) -> None:
        super().__init__()
        self.id = id if id else str(uuid.uuid4())
        self.minio_fs = minio_fs if minio_fs else get_minio_fs()

    def save_checkpoint(
        self,
        checkpoint: Dict[str, Any],
        path: _PATH,
        storage_options: Optional[Any] = None,
    ) -> None:
        buffer = BytesIO()
        torch.save(checkpoint, buffer)
        path = self.model_path(path)

        with self.minio_fs.open(path, "wb") as f:
            f.write(buffer.getvalue())

    def load_checkpoint(
        self,
        path: _PATH,
        map_location: Optional[Callable] = lambda storage, loc: storage,
    ) -> Dict[str, Any]:

        path = self.model_path(path)
        if not self.minio_fs.exists(path):
            raise FileNotFoundError(f"Checkpoint file {path} not found")
        else:
            with self.minio_fs.open(path, "rb") as f:
                return torch.load(f, map_location=map_location)

    def remove_checkpoint(self, path: _PATH) -> None:
        path = self.model_path(path)
        if not self.minio_fs.exists(path):
            raise FileNotFoundError(f"Checkpoint file {path} not found")
        else:
            self.minio_fs.delete(path)

    def model_path(self, path: _PATH) -> _PATH:
        bucket = MinioBuckets.MODELS.value
        cp_path = path.split(os.sep)[-1]
        path = f"{bucket}/{self.id}/{cp_path}"
        return path
