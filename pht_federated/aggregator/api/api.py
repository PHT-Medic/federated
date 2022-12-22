from fastapi import APIRouter

from pht_federated.aggregator.api.endpoints import discovery, proposals, protocol

api_router = APIRouter()

# Include the routers defined in the endpoints file in the main api

api_router.include_router(discovery.router, prefix="/proposal", tags=["Discovery"])
api_router.include_router(proposals.router, prefix="/proposal", tags=["Proposal"])
api_router.include_router(protocol.router, prefix="/protocol", tags=["Protocol"])
