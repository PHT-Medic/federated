import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Proposal(BaseModel):
    id: Optional[uuid.UUID]
    name: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class ProposalCreate(Proposal):
    pass


class ProposalUpdate(Proposal):
    pass
