[![CI](https://github.com/PHT-Medic/federated/actions/workflows/main_ci.yml/badge.svg)](https://github.com/PHT-Medic/federated/actions/workflows/main_ci.yml)
[![codecov](https://codecov.io/gh/PHT-Medic/federated/branch/main/graph/badge.svg?token=Q2JA1VOYK9)](https://codecov.io/gh/PHT-Medic/federated)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
# PHT Medic Federated

This project contains all python code for the PHT-Medic Federated Learning project grouped into several packages.
- `protocols`: contains the cryptographic functionality required for the supported protocols
- `aggregator`: contains the aggregator REST API implementation, and server side storage for running protocols
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


## Contributing

Create a branch/fork the repository and create a pull request to the `main` branch to contribute to the project.
The CI pipeline will run all tests and checks on the code, before it can be merged.

### pre-commit hooks
To ensure a consistent code style and to prevent common mistakes, we use [pre-commit](https://pre-commit.com/) hooks.
To install the hooks run `pre-commit install` in the root folder of the project with the virtual environment activated
and the dev dependencies installed.

### Code style
This project uses [black](https://black.readthedocs.io/) for code formatting.
Run to format your code before pushing it to the remote repository.
```shell
black .
```

Linting is done with [flake8](https://flake8.pycqa.org/en/latest/).
Linting is configured in the pre-commit hooks and will be run automatically before commiting.
if you want to run the linter manually run
```shell
flake8 . --max-line-length=127 --ignore=E203,W503
```


## Protocol

Mask based secure aggregation protocol. Implementation and extension of the paper 
[Practical Secure Aggregation for Privacy-Preserving Machine Learning](https://dl.acm.org/doi/10.1145/3133956.3133982)

