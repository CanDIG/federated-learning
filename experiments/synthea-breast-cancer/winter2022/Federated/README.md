# Improved Federated Experimental Setup with the Synthea Synthetic Breast Cancer Dataset

## Background
As in the fall 2021 folder, this experiment uses a docker-compose file generated by `orchestration-scripts/configure_docker_compose.py`.

The files modified have been moved already for convenience. If any futher modification are performed to the files in this folder, replace the following:
- `services/fl-client/client.py` with `experiments/synthea-breast-cancer/winter2022/Federated/fl-services/client.py`
- `services/fl-server/server.py` with `experiments/synthea-breast-cancer/winter2022/Federated/fl-services/server.py`
- `services/fl-client/utils.py` with `experiments/synthea-breast-cancer/winter2022/Federated/fl-services/utils.py`
- `services/fl-server/utils.py` with `experiments/synthea-breast-cancer/winter2022/Federated/fl-services/utils.py`
- `services/fl-server/helpers` with `experiments/synthea-breast-cancer/winter2022/Federated/fl-services/helpers`
- `services/fl-client/helpers` with `experiments/synthea-breast-cancer/winter2022/Federated/fl-services/helpers`

## How to Run

First, make sure that all submodules have been recursively updated by running
```
git submodule update --init --recursive
```

You can run the experimental setup by ensuring you have a copy of the 10yrs Synthea mCODE data installed on your machine, and then using the quickstart script to set up instances of the services needed.
Eg. Let's say the 10yrs directory is in the root federated-learning folder. Then from the root federated-learning folder, perform:

```
./experiments/synthea-breast-cancer/winter2022/Federated/quickstart.sh -i -s 10yrs/female 3 5000
```

This will generate 3 clients and 1 server, alongside ingesting the 10yrs/female data into an instance of Katsu, accessible through the GraphQL-interface generated. This will take quite a long time, up to 35 minutes if ingesting the data as well.
Use the `-h`flag with the `quickstart.sh` script for further information on the arguements. 

## Further Notes

This is the federated implementation of the [Non-Federated Logisitic Regression](../Non-Federated/SyntheaClassifiers.ipynb) Classifier. The full explanation on the choice of classifiers can be found in the [Synthea Breast Cancer Dataset - Federation](Synthea Breast Cancer Dataset - Federation) document.