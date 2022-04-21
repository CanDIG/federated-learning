# federated-learning
For the development of differentially private federated machine learning on the CanDIG data services.

<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [federated-learning](#federated-learning)
  - [Quick Start](#quick-start)
  - [Dependencies](#dependencies)
  - [Running a Federated Learning Experiment](#running-a-federated-learning-experiment)
    - [Generating an experiment](#generating-an-experiment)
    - [Running an experiment](#running-an-experiment)
  - [Contributing](#contributing)

<!-- /code_chunk_output -->

## Quick Start

1. **Pull submodule updates**
    - The `federated-learning` repository relies on various other repositories for providing the backend data services, interfaces, and training data. From the root of this repo, pull these repositories with `git submodule update --init --recursive`
2. **Configure environment**
    - The `docker-compose.yml` file expects a `.env` file in root folder, so that it can configure the Katsu database with some secrets such as the password. For a generic configuration, you can run the following to copy and use the default configuration: `cp .default.env .env`
3. **Start Experiment**
    - Use a quickstart script to start your federated experiment if you have one present. Otherwise, proceed with the following:
        - Create a `docker-compose` file with [`orchestration-scripts/configure_docker_compose.py`](orchestration-scripts/configure_docker_compose.py).
        - Spin up docker: `docker-compose up -d`

## Dependencies

CanDIGv2 submodules:
1. [Katsu](https://github.com/CanDIG/katsu/) serves clinical data that the Federated-Learning services may train on and classify
2. [GraphQL-interface](https://github.com/CanDIG/GraphQL-interface) fetches data from Katsu and serves it to the Federated-Learning services in the Graph Query Language, greatly reducing the amount of preprocessing code required for running an experiment.

Datasets:
1. Taken from the Synthea/CodeX [synthetic patient mCODE datasets](https://confluence.hl7.org/display/COD/mCODE+Test+Data), the 10yrs breast cancer dataset downloadable [here](http://hdx.mitre.org/downloads/mcode/mcode1_0_10yrs.zip) is used in all of the federated learning experiments included in this repository.
2. The [MoHCCN-data](https://github.com/CanDIG/mohccn-data) synthetic dataset was used for some early non-federated experiments.

## Running a Federated Learning Experiment

In the future, we would like to provide to the user:
- an assortment of federated learning experiments that can be run on the data stored in CanDIG's data services, along with
- an API for selecting the experiment and specifying its configurable parameters.

However, at this stage in development, the federated-learning services expect the user to:
- provide the source code for the experiment that they want to run, and
- run the experiment using the docker CLI.

Several example experiments are available in the `experiments/synthea-breast-cancer` subdirectory, or you may provide your own.

### Generating an experiment

To make another experiment, create an `experiment` folder like the one in the `experiments/mock-experiment/` subdirectory or like the [synthea experiments folder](https://github.com/CanDIG/federated-learning/tree/DIG-807-Injected-Experiments/experiments/mock-experiment). Place this experiment folder inside another experiment subdirectory within the larger `experiments` root subdirectory (eg. `experiments/my-new-experiment/experiment/`). 
Ensure that there are at least the 6 files present in the example folder, within your folder.
- `__init__.py`
- `experiment.py`
- `flower_client.py`
- `get_eval_fn.py`
- `model.py`
- `settings.py`

If there are any supplementary functions required, create a `helpers` folder in the same subdirectory. Visit the [`experiments/README.md`](experiments/README.md) file for more information.

### Running an experiment

In order to run the experiment, it makes the most sense to create your own `quickstart.sh` script to get the required docker services up in order, with the parameters you need. For example, for the Winter 2022 Synthea federated experiment, use the following line of code from the root of the federated learning directory:

```bash
./experiments/synthea-breast-cancer/winter2022/Federated/quickstart.sh -i <INGEST-PATH> -p <PORT> -n <SITES> -r <ROUNDS> -e <PATH-TO-EXPERIMENTS-DIRECTORY>
```

Perform the following to get help for the quickstart script:

```bash
./experiments/synthea-breast-cancer/winter2022/Federated/quickstart.sh -h
```

If an options is not called, the script uses the following default values:
- no `-i`: Will not ingest data
- no `-p`: Will use port `5000`
- no `-n`: Will generate `2` client sites
- no `-r`: Will run the experiment for `100` rounds
- no `-e`: Will look for an `./experiment` directory
- no `-s`: Will not put all of the data into one dataset

## Technical debt

To prepare the federated-learning services for deployment, there should be a set of models (or a carefully-parametrized model-building pipeline) prepared and packaged into the docker containers. An API should be provided for selecting and running these models. This API should then be connected to Tyk.

Additionally, improvements should be made to the [GraphQL-interface](https://github.com/CanDIG/GraphQL-interface) that the federated-learning services depend on for data. The data services (Katsu and the variants service) should ideally expose their own GraphQL APIs, eliminating the need for a GraphQL-interface. Alternately, improvements in training speed could be achieved by refactoring the existing GraphQL-interface proof-of-concept to use concurrency, although this is not an optimal long-term solution.

The Flower framework for federated learning used by this repository will soon support communications over secure gRPC; this repository and/or its deployment should be upgraded accordingly.

### Improving differential privacy

Suggestions for implementing a more thorough differential privacy setup are provided in `docs/FL_differential_privacy.md`.

## Contributing

Currently, the federated-learning services have only been run on clinical data stored in Katsu. To add more data services, add the services to the `docker-compose.yml` file (as well as the `configure_docker_compose.py` file) and add their default configuration variables to `.default.env`. You may also wish to add ingestion scripts to the `ingestion-scripts` subdirectory.

All experiment-specific source code should go in the `experiments` subdirectory.

To run experiments on a different dataset, see the `experiments/mock-experiment/template-quickstarts` directory for template quickstart files for both `federated` and `differentially-private federated` experiments. These templates are not mandatory to use, if they are not convenient you may ignore or even remove them.