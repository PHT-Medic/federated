[![CI](https://github.com/PHT-Medic/federated/actions/workflows/main_ci.yml/badge.svg)](https://github.com/PHT-Medic/federated/actions/workflows/main_ci.yml)
[![codecov](https://codecov.io/gh/PHT-Medic/federated/branch/main/graph/badge.svg?token=Q2JA1VOYK9)](https://codecov.io/gh/PHT-Medic/federated)

# PHT Medic Federated

This project contains all python code for the PHT-Medic Federated Learning project grouped into several packages.
- `protocol`: contains the cryptographic functionality required for the aggregation protocol
- `aggregator`: contains the aggregator REST API implementation
- `client`: implements a client to be used with the aggregator API
- `trainer`: contains the code for the client side training of models


# Installation
Clone the repository and navigate into the root folder. Run
```shell
pip install -e .
```

## Development

If [Pipenv](https://pipenv.pypa.io/en/latest/) is not installed follow the instruction [here](https://pipenv.pypa.io/en/latest/).

Open a shell at the root of the project and activate the virtual environment with `pipenv shell`.  
Install the dependencies with `pipenv install --dev`.


### Start development services
to spin up all services run `docker compose up -d` in the root folder.
```shell
docker compose up -d
```

If you want to start a specific service run `docker compose up -d <service_name>`, with the name defined in the compose file.

Start the [fastapi](https://fastapi.tiangolo.com/) aggregator service with hot reloading using [uvicorn](https://www.uvicorn.org/):

#### Database
When using the postgres db defined in the compose file, two databases are created. One to use for development and a
separate one for testing. The databases are created with the name `aggregator` and `aggregator_test` respectively.
The creation of these database is defined in the `/scripts/init.sql` file.


### Run the aggregator

The aggregator can be started in development mode with hot reloading using the following command:

```shell
uvicorn pht_federated.aggregator.app:app --reload --port 8000 --host 0.0.0.0
```


## Protocol

Mask based secure aggregation protocol. Implementation and extension of the paper 
[Practical Secure Aggregation for Privacy-Preserving Machine Learning](https://dl.acm.org/doi/10.1145/3133956.3133982)

