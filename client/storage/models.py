import fsspec
from torch import load

from client.storage import MinioBuckets


def load_model_checkpoint(fs: fsspec.AbstractFileSystem, model_name: str, checkpoint_path: str):
    bucket = MinioBuckets.MODELS.value
    path = f"{bucket}/{model_name}/{checkpoint_path}"

    with fs.open(path, 'rb') as f:
        model_data = load(f)

    return model_data


def list_checkpoints(fs: fsspec.AbstractFileSystem, model_name: str):
    pass
