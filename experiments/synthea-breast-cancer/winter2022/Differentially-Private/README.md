# Differentially-Private Federated Experimental Setup with the Synthea Synthetic Breast Cancer Dataset

## Background
As in the fall 2021 folder, this experiment uses a docker-compose file generated by `orchestration-scripts/configure_docker_compose.py`.

This experiment makes use of the `diffprivlib` module, an [IBM project](https://github.com/IBM/differential-privacy-library), to implement differentially private federated-learning, as discussed in this [confluence document](https://candig.atlassian.net/wiki/spaces/CA/pages/634224664/Synthea+Breast+Cancer+-+Choice+of+Differential+Privacy+Algorithm). For differentially-private Logistic Regression, the `diffprivlib` module makes use of the "[*`Vector`*](https://github.com/IBM/differential-privacy-library/blob/main/diffprivlib/models/logistic_regression.py) mechanism, which adds a Laplace-distributed random vector to the objective". This differential privacy library acts on the fl-client level, adding noise whenever a model is going to be fitted. The federation library is still the same, flower, and it implements federation through the `Federated Averaging` Algorithm. Although end-to-end differentially-private algorithms, like Nikolaos Tatarakis' proposed algorithm in his thesis titled "Differentially Private Federated Learning" were considered, as noted in the aforementioned Confluence document, those models were disregarded because of the time needed to implement them.

The epsilon was modified to be 0.85, the default is 1.0 for `diffprivlib` models, but this is not sufficiently private. 

## How to Run

Given the similarities to the Non-Differentially Private Federated Experiment, we used the `experiment` folder from that experiment as the base for this experiment. This results in a reduction of repeated code, but comes with the drawback of not being able to use docker volumes and so for this experiment, we must rebuild the container for each new trial we wish to perform. We must specify the path to the federated `experiment` folder, with the `-f` flag, when calling the script, so that the script can add its files to the docker containers.

First, make sure that all submodules have been recursively updated by running
```
git submodule update --init --recursive
```

You can run the experimental setup by ensuring you have a copy of the 10yrs Synthea mCODE data installed on your machine, and then using the quickstart script to set up instances of the services needed.
Eg. Let's say the 10yrs directory is in the root federated-learning folder. Then from the root federated-learning folder, perform:

```bash
./experiments/synthea-breast-cancer/winter2022/Differentially-Private/quickstart.sh -i 10yrs/female -e <DP_EXPERIMENT_PATH> -f <ORIGINAL_EXPERIMENT_PATH>
```

This will generate 2 clients and 1 server, alongside ingesting the 10yrs/female data into an instance of Katsu, accessible through the GraphQL-interface generated. This will take quite a long time, up to 35 minutes if ingesting the data as well.
Use the `-h` flag with the `quickstart.sh` script for further information on the arguments. 

## Further Notes

This is the  differentially private federated implementation of the [Non-Federated Logisitic Regression](../Non-Federated/SyntheaClassifiers.ipynb) Classifier. The full explanation on the choice of classifiers can be found in the [Synthea Breast Cancer Dataset - Federation](Synthea Breast Cancer Dataset - Federation) document. The implementation without the differential privacy can be found in the [Federated folder](../Federated).