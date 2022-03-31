# federated-learning
For the development of differentially private federated machine learning on the CanDIG data services

<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

## Quick Start

1. **Pull submodule updates.** The `federated-learning` repository relies on various other repositories for providing the backend data services, interfaces, and training data. From the root of this repo, pull these repositories with `git submodule update --init --recursive`
1. **Configure docker-compose.** The `docker-compose.yaml` file expects a `.env` file in root folder, so that it can configure the Katsu database with some secrets such as the password. For a generic configuration, you can run the following to copy and use the default configuration: `cp .default.env .env`
3. **Spin up Katsu.** Run `docker-compose up katsu`
4. **Browse Katsu.** Navigate your browser to `localhost:8000`
5. **Query Katsu** by GETting from `localhost:8000/api/mcodepackets`. There will be zero results (`"count": 0`) prior to ingest, and a number of results equal to the dataset size following ingest.

## Creating a New Federated Learning Experiment

### Generating an experiment

To make another experiment, create an `experiment` folder like the one in the `experiments/mock-experiment/` subdirectory or like the [synthea experiments folder](https://github.com/CanDIG/federated-learning/tree/DIG-807-Injected-Experiments/experiments/mock-experiment). Place this experiment folder inside another experiment subdirectory within the larger `experiments` root subdirectory (eg. `experiments/my-new-experiment/experiment/`). 
Ensure that there are at least the 5 files present in the example folder, within your thr folder.
- `\_\_init\_\_.py`
- `experiment.py`
- `flower_client.py`
- `get_eval_fn.py`
- `model.py`
If there are any supplementary functions required, create a `helpers` folder in the same subdirectory.

### Running an experiment

In order to run the experiment, use the following line of code from the root of the federated learning directory:

```bash
./experiments/synthea-breast-cancer/winter2022/Federated/quickstart.sh -i <INGEST-PATH> -p <PORT> -n <SITES> -r <ROUNDS> -e <PATH-TO-EXPERIMENTS-DIRECTORY>
```

Perform the following to get help for the quickstart script:

```bash
./experiments/synthea-breast-cancer/winter2022/Federated/quickstart.sh -h
```

If none of the options are selected, the script uses the following default values:
- `-i`: Will not ingest data
- `-p`: Will use port `5000`
- `-n`: Will generate `2` client sites
- `-r`: Will run the experiment for `100` rounds
- `-e`: Will look for an `./experiment` directory
- `-s`: Will not put all of the data onto one dataset

## Development

To run more existing services alongside Katsu, add the services to the `docker-compose.yaml` file and add their default configuration variables to `.default.env`.

You can also contribute code pertaining to federated learning to this repository. Please organize new files into subdirectories. The root folder should only contain the README, configuration files, and subdirectories.
