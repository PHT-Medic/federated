from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid



class Proposals(BaseModel):
    id: Optional[uuid.UUID]
    name: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class ProposalsCreate(Proposals):
    pass


class ProposalsUpdate(Proposals):
    pass
