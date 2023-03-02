import os

import httpx
import pytest
from authup import Authup
from authup.plugins.httpx import AuthupHttpx
from dotenv import load_dotenv, find_dotenv


@pytest.fixture(scope="session", autouse=True)
def authup_instance():
    load_dotenv(find_dotenv())
    authup = Authup(
        url=os.getenv("AUTH_URL"),
        username=os.getenv("ADMIN_USER"),
        password=os.getenv("ADMIN_PASSWORD"),
    )
    return authup


@pytest.fixture(scope="session")
def robot_creds(authup_instance):
    secret = os.getenv("ROBOT_SECRET")

    auth = AuthupHttpx(
        url=authup_instance.settings.url,
        username=authup_instance.settings.username,
        password=authup_instance.settings.password.get_secret_value(),
    )

    r = httpx.get(authup_instance.settings.url + "/robots", auth=auth)

    robot_id = r.json()["data"][0]["id"]

    return robot_id, secret
