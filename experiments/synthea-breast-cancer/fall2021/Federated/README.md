# A Federated Experimental Setup with the Synthea Synthetic Breast Cancer Dataset

Running this experimental setup is straightforward. First, make sure that all submodules have been recursively updated by running
```
git submodule update --init --recursive
```
Then, *from the root level of the `federated-learning` repository*, run `quickstart.sh`, providing the only arguments as the absolute path of the [Synthea/CodeX breast cancer dataset](https://confluence.hl7.org/display/COD/mCODE+Test+Data) on your local machine and the number of sites/instances you want (we recommend 2).
```
bash examples/synthea-breast-cancer/Federated/quickstart.sh <PATH_TO_SYNTHEA_DSET> <NUM_SITES>
```

After a long ingestion process (~10 minutes), the script will terminate the docker-compose service. 
Restarting with `docker-compose up` will allow you to view a completed federated learning training process in action, for 100 rounds of training between the clients on the same training data per site.

Allow the server and clients approximately 1 minute to finish querying and preprocessing data from the GraphQL interface before training begins.

The data preprocessing follows the same procedure as in `Non-FederatedClassification.ipynb`, so there is not much data to work with due to poor class distribution in the Synthea dataset
for this particular experimental setup. You should see the accuracy and AUC score of the classifier stay at constant values (0.6 and 0.71, but this may vary on random seeds) for every round past the 2nd, with the loss tapering off very quickly (as soon as the 3rd round).

This particular demo showcases how federated learning *can* be run on the CanDIG microservices architecture, but a stronger experimental setup is required to truly investigate feasibility and
true gains/losses due to learning from oncological data in this decentralized manner.
