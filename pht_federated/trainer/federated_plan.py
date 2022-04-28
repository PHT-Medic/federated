import uuid
from typing import Optional

from pydantic import BaseModel


class HyperParameters(BaseModel):
    # todo add more hyper parameters
    learning_rate: float
    # todo dynamic distributed batch size
    batch_size: int
    early_stopping_patience: Optional[int] = None
    early_stopping_delta: Optional[float] = None

    @classmethod
    def default(cls):
        return cls(
            learning_rate=0.001,
            batch_size=32,
            early_stopping_patience=3,
            early_stopping_delta=0.001,
        )


class FederatedParameters(BaseModel):
    # todo add more federated parameters / choose algorithm
    num_clients: Optional[int] = None
    num_epochs: Optional[int] = None
    warmup_epochs: Optional[int] = None
    warmup_batches: Optional[int] = None
    warmup_learning_rate: Optional[float] = None

    @classmethod
    def default(cls):
        return cls(
            num_clients=None,
            num_epochs=20,
            warmup_epochs=2,
            warmup_batches=None,
            warmup_learning_rate=0.001,
        )


class FederatedPlan(BaseModel):
    """
    A federated plan describes the federated training of a model.
    """
    id: Optional[str] = None
    hyper_params: Optional[HyperParameters] = None
    federated_params: Optional[FederatedParameters] = None

    @classmethod
    def default(cls):
        return cls(
            id=str(uuid.uuid4()),
            hyper_params=HyperParameters.default(),
            federated_params=FederatedParameters.default()
        )
