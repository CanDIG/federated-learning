# federated-learning
For the development of differentially private federated machine learning on the CanDIG data services.

<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

## Quick Start

1. **Pull submodule updates**
    - The `federated-learning` repository relies on various other repositories for providing the backend data services, interfaces, and training data. From the root of this repo, pull these repositories with `git submodule update --init --recursive`
2. **Configure environment**
    - The `docker-compose.yml` file expects a `.env` file in root folder, so that it can configure the Katsu database with some secrets such as the password. For a generic configuration, you can run the following to copy and use the default configuration: `cp .default.env .env`
3. **Start Experiment**
    - Use a quickstart script to start your federated experiment if you have one present. Otherwise, proceed with the following:
        - Create a `docker-compose` file with [`orchestration-scripts/configure_docker_compose.py`](orchestration-scripts/configure_docker_compose.py).
        - Spin up docker: `docker-compose up -d`

## Creating a New Federated Learning Experiment

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

In order to run the experiment, it makes the most sense to create your own `quickstart.sh` script to get the required docker services up in order, with the parameters you need. For example, for the Winter 2022 Synthea federated experiment, use the follwing line of code from the root of the federated learning directory:

```bash
./experiments/synthea-breast-cancer/winter2022/Federated/quickstart.sh -i <INGEST-PATH> -p <PORT> -n <SITES> -r <ROUNDS> -e <PATH-TO-EXPERIMENTS-DIRECTORY>
```

Perform the following to get help for the quickstart script:

```bash
./experiments/synthea-breast-cancer/winter2022/Federated/quickstart.sh -h
```

If none of the options are given, the script uses the following default values:
- `-i`: Will not ingest data
- `-p`: Will use port `5000`
- `-n`: Will generate `2` client sites
- `-r`: Will run the experiment for `100` rounds
- `-e`: Will look for an `./experiment` directory
- `-s`: Will not put all of the data onto one dataset

## Development

To run more existing services alongside Katsu, add the services to the `docker-compose.yml` file (as well as the `configure_docker_compose.py` file) and add their default configuration variables to `.default.env`.

You can also contribute code pertaining to federated learning to this repository. Please organize new files into subdirectories. The root folder should only contain the README, configuration files, and subdirectories.
