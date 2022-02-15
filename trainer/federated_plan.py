from typing import Optional

from pydantic import BaseModel


class HyperParameters(BaseModel):
    learning_rate: float
    batch_size: int


class FederatedParameters(BaseModel):
    num_clients: int
    num_epochs: int
    warmup_epochs: Optional[int] = None
    warmup_batches: Optional[int] = None
    warmup_learning_rate: Optional[float] = None


class FederatedPlan(BaseModel):
    """
    A federated plan describes the federated training of a model.
    """
    id: Optional[str] = None
    hyper_params: Optional[HyperParameters] = None
    federated_params: Optional[FederatedParameters] = None
