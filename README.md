[![CI](https://github.com/PHT-Medic/federated/actions/workflows/main_ci.yml/badge.svg)](https://github.com/PHT-Medic/federated/actions/workflows/main_ci.yml)
# PHT Medic Federated Learning

This project contains all python code for the PHT-Medic Federated Learning project grouped into several modules.
- `protocol`: contains the crypto code for the aggregation protocol
- `client`: contains the code for the client
- `aggregator`: contains the code for the aggregator
- `trainer`: contains the code for the federated trainer

# Installation
Clone the repository and navigate into the root folder. Run
```shell
pip install -e .
```

## Development

If [Pipenv](https://pipenv.pypa.io/en/latest/) is not installed follow the instruction [here](https://pipenv.pypa.io/en/latest/).

Open a shell at the root of the project and activate the virtual environment with `pipenv shell`.  
Install the dependencies with `pipenv install --dev`.

## Pytorch install



## Protocol

Mask based secure aggregation protocol. Implementation and extension of the paper 
[Practical Secure Aggregation for Privacy-Preserving Machine Learning](https://dl.acm.org/doi/10.1145/3133956.3133982)

