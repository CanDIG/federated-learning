# Adapted from https://github.com/adap/flower/tree/main/examples/sklearn-logreg-mnist

import os
SERVER_URL = os.environ['FLOWER_SERVER_URL']

import warnings
import flwr as fl
import numpy as np

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.metrics import roc_auc_score

import utils

if __name__ == "__main__":
    (X_train, y_train), (X_test, y_test) = utils.load_data()

    # Create LogisticRegression Model
    model = LogisticRegression(
        solver='liblinear',
        tol=0.01,
        C=0.1,
        random_state=1729,
        multi_class='ovr',
        max_iter=10,  # local epoch
        warm_start=True,  # prevent refreshing weights when fitting
    )

    # Setting initial parameters, akin to model.compile for keras models
    utils.set_initial_params(model)

    # Define Flower client
    class MnistClient(fl.client.NumPyClient):
        def get_parameters(self):  # type: ignore
            return utils.get_model_parameters(model)

        def fit(self, parameters, config):  # type: ignore
            utils.set_model_params(model, parameters)
            # Ignore convergence failure due to low local epochs
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model.fit(X_train, y_train)
            print(f"Training finished for round {config['rnd']}")
            return utils.get_model_parameters(model), len(X_train), {}

        def evaluate(self, parameters, config):  # type: ignore
            utils.set_model_params(model, parameters)
            loss = log_loss(y_test, model.predict_proba(X_test))
            accuracy = model.score(X_test, y_test)
            auc_score = roc_auc_score(y_test, model.predict(X_test))
            return loss, len(X_test), {"accuracy": accuracy, "auc_score": auc_score}

    # Start Flower client
    fl.client.start_numpy_client(SERVER_URL, client=MnistClient())