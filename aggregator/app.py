from concurrent import futures
import logging

import grpc
from aggregator.proto import aggregator_pb2_grpc, aggregator_pb2


class Aggregator(aggregator_pb2_grpc.AggregatorServicer):

    def __init__(self):
        print("Aggregator server started")
        super().__init__()

    def SubmitMaskedInput(self, request, context):
        print(request)
        return aggregator_pb2.MaskedInputResponse(
            train_id=request.train_id,
            success=True,
            aggregate_available=False,
        )

    def DistributeAggregatedInput(self, request, context):
        print(request)
        return aggregator_pb2.AggregatedInputResponse(
            train_id=request.train_id,
            success=False,
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    aggregator_pb2_grpc.add_AggregatorServicer_to_server(Aggregator(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()