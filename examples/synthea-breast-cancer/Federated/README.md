# A Federated Experimental Setup with the Synthea Synthetic Breast Cancer Dataset

Running this experimental setup is straightforward. First, make sure that all submodules have been recursively updated by running
```
git submodule update --init --recursive
```
Then, *from the root level of the `federated-learning` repository*, run `quickstart.sh`, providing the only argument as the absolute path of the Synthea dataset on your local machine.
```
bash examples/synthea-breast-cancer/Federated/quickstart.sh <PATH_TO_SYNTHEA_DSET>
```

After a long ingestion process (~10 minutes), the script will terminate the docker-compose service. 
Restarting with `docker compose up` will allow you to view a completed federated learning training process in action, for 100 rounds of training between two clients on the same training data per site.

Allow the server and clients approximately 1 minute to finish querying and preprocessing data from the GraphQL interface before training begins.

The data preprocessing follows the same procedure as in `Non-FederatedClassification.ipynb`, so there is not much data to work with due to poor class distribution in the Synthea dataset
for this particular experimental setup. You should see the accuracy of the classifier stay at a constant value (between 0.6 and 0.71 depending on random seed) for every round past the 2nd, with the loss tapering off very quickly (as soon as the 3rd round).

This particular demo showcases how federated learning *can* be run on the CanDIG microservices architecture, but a stronger experimental setup is required to truly investigate feasibility and
true gains/losses due to learning from oncological data in this decentralized manner.

