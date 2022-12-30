import uuid

from pht_federated.protocols.secure_aggregation import ClientProtocol
from pht_federated.protocols.secure_aggregation.models.server_messages import (
    BroadCastClientKeys,
    ServerKeyBroadcast,
)
from pht_federated.protocols.secure_aggregation.secrets.ciphers import decrypt_cipher
from pht_federated.protocols.secure_aggregation.secrets.util import load_public_key


def test_ciphers():
    protocol = ClientProtocol()
    keys_1, broadcast_1 = protocol.setup()
    keys_2, broadcast_2 = protocol.setup()

    sender = "test-sender"
    receiver = "test-receiver"

    server_broadcast = ServerKeyBroadcast(
        protocol_id=uuid.uuid4(),
        round_id=0,
        participants=[
            BroadCastClientKeys(client_id=sender, broadcast=broadcast_1),
            BroadCastClientKeys(client_id=receiver, broadcast=broadcast_2),
        ]
    )
    seed_1, share_msg_1 = protocol.process_key_broadcast(
        client_id=sender, keys=keys_1, broadcast=server_broadcast, k=2
    )
    seed_2, share_msg_2 = protocol.process_key_broadcast(
        client_id=receiver, keys=keys_2, broadcast=server_broadcast, k=2
    )

    cipher = share_msg_1.ciphers[0]

    assert cipher.recipient == receiver

    decrypted_cipher = decrypt_cipher(
        recipient=receiver,
        recipient_key=keys_2.cipher_key,
        sender_key=load_public_key(broadcast_1.cipher_public_key),
        sender=sender,
        encrypted_cypher=cipher.cipher,
    )

    assert decrypted_cipher.sender == sender
    assert decrypted_cipher.recipient == receiver
    assert decrypted_cipher.key_share

    print(share_msg_1)
    print(share_msg_2)
