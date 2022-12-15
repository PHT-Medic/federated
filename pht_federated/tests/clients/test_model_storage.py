# import pytest
# from pht_federated.clients.storage import get_minio_fs
# from pht_federated.clients.storage import models
# from dotenv import load_dotenv, find_dotenv

#
# @pytest.fixture()
# def minio_fs():
#     load_dotenv(find_dotenv())
#     return get_minio_fs()
#
#
# def test_load_model_checkpoint_minio(minio_fs):
#     test_model_id = "2f4bd5a9-8405-4455-8923-70f9d6d1c8db"
#     test_check_point_file = "epoch=0-step=937.ckpt"
#
#     model = models.load_model_checkpoint(minio_fs, test_model_id, test_check_point_file)
#
#     assert model
#     assert isinstance(model, dict)
#     for i, v in model["state_dict"].items():
#         print(i, v)
