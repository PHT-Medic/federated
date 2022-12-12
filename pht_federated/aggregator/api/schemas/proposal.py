from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid



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
