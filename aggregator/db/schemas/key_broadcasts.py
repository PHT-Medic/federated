from typing import Optional

from sqlmodel import Field, SQLModel

class ClientKeyBroadcasts(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    train_id: str
    client_id: str
    iteration: int
    cipher_key: str
    sharing_key: str
    signature: Optional[str] = None


