from __future__ import print_function

import logging

import grpc
from pht_federated.aggregator import aggregator_pb2, aggregator_pb2_grpc
import asyncio


def submit_masked_input(masked_input: aggregator_pb2.MaskedInput) -> aggregator_pb2.MaskedInputResponse:
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = aggregator_pb2_grpc.AggregatorStub(channel)
        response = stub.SubmitMaskedInput(masked_input)

    return response


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = aggregator_pb2_grpc.AggregatorStub(channel)
        response = stub.SubmitMaskedInput(aggregator_pb2.MaskedInput(
            client_id='test_client',
            train_id="test_train",
            input=[aggregator_pb2.Parameters(
                id="test",
                name="test",
                value=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
            )]
        ))

    print("Aggregator response: ", response)


if __name__ == '__main__':
    logging.basicConfig()
    run()
