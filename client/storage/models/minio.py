import os

from dotenv import load_dotenv, find_dotenv
import s3fs

MODEL_BUCKET = 'models'
MODEL_PREFIX = 'model-'


def store_model_checkpoint(model_name, model_data):
    pass


def save_model(model_name, model_data):
    pass


def get_model(model_name):
    pass


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    minio = os.getenv("MINIO_ACCESS_KEY")
    fs = s3fs.S3FileSystem(anon=False,
                           key=os.getenv("MINIO_ACCESS_KEY"),
                           secret=os.getenv("MINIO_SECRET_KEY"),
                           use_ssl=True,
                           client_kwargs={'endpoint_url': f'https://{os.getenv("MINIO_URL")}'})
    print(fs.ls(MODEL_BUCKET))
    print(fs.open(f"{MODEL_BUCKET}/upload.py", 'rb').read())
