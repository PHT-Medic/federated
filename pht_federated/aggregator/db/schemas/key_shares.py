from typing import Optional

from sqlmodel import Field, SQLModel


class KeyShares(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    train_id: str
    iteration: int
    sender_id: str
    receiver_id: str
    key_share: str
