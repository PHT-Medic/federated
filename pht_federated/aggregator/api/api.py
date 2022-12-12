from fastapi import APIRouter
from pht_federated.aggregator.api.endpoints import discovery
from pht_federated.aggregator.api.endpoints import proposals

api_router = APIRouter()

# Include the routers defined in the endpoints file in the main api

api_router.include_router(discovery.router, prefix="/discovery", tags=["Discovery"])
api_router.include_router(proposals.router, prefix="/proposal", tags=["Proposal"])


