from typing import List
from sqlalchemy.orm import Session

from pht_federated.aggregator.models import protocol as models

def get_key_broadcasts_for_round(db: Session, round_id: int) -> List[models.ClientKeyBroadcast]:
    return db.query(
        models.ClientKeyBroadcast
    ).filter(
        models.ClientKeyBroadcast.round_id == round_id,
    ).all()


