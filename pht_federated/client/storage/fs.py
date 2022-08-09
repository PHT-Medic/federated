import os
import enum

import fsspec
import s3fs


class MinioBuckets(enum.Enum):
    MODELS = 'models'
    DATASETS = 'discoveries'


def get_minio_fs(minio_url: str = None, access_key: str = None, secret_key: str = None) -> s3fs.S3FileSystem:
    """
    Initialize a minio filesystem object.
    :param minio_url:
    :param access_key:
    :param secret_key:
    :return:
    """

    if minio_url is None:
        minio_url = os.getenv("MINIO_URL")

    assert minio_url is not None, "MINIO_URL is not set"

    if access_key is None:
        access_key = os.getenv("MINIO_ACCESS_KEY")

    if secret_key is None:
        secret_key = os.getenv("MINIO_SECRET_KEY")

    fs = s3fs.S3FileSystem(anon=False,
                           key=access_key,
                           secret=secret_key,
                           use_ssl=True,
                           client_kwargs={'endpoint_url': f'https://{minio_url}'})
    return fs


def get_fs(path):
    """
    Get a filesystem object for the given path.
    """
    if path.startswith("s3://"):
        return s3fs.S3FileSystem(anon=True)
    else:
        return fsspec.filesystem("file")
