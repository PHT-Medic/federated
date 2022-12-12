from pht_federated.clients.storage import get_minio_fs
from dotenv import load_dotenv, find_dotenv


def test_model_serialization():
    test_model_id = "2f4bd5a9-8405-4455-8923-70f9d6d1c8db"
    test_check_point_file = "epoch=0-step=937.ckpt"
    load_dotenv(find_dotenv())
    fs = get_minio_fs()




