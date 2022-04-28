from sqlmodel import Session

from pht_federated.protocol import ServerProtocol
from pht_federated.protocol.models.client_messages import ClientKeyBroadCast, ShareKeysMessage, MaskedInput, UnmaskShares

server_protocol = ServerProtocol()


class AggregatorService:

    def process_key_broadcast(self, db: Session, key_broadcast: ClientKeyBroadCast):
        pass

    def process_cipher_broadcast(self, db: Session, cipher_broadcast: ShareKeysMessage):
        pass

    def process_masked_input(self, db: Session, masked_input: MaskedInput):
        pass

    def process_unmask_shares(self, db: Session, unmask_shares: UnmaskShares):
        pass


    def _update_round_0_status(self, db: Session, train_id: str, key_broadcast: ClientKeyBroadCast):
        pass
