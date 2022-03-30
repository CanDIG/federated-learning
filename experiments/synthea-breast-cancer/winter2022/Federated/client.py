# Adapted from https://github.com/adap/flower/tree/main/examples/sklearn-logreg-mnist

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, balanced_accuracy_score, f1_score, matthews_corrcoef
import flwr as fl
import warnings
import utils
import os

SERVER_URL = os.environ['FLOWER_SERVER_URL']

if __name__ == "__main__":
    (X_train, y_train), (X_test, y_test) = utils.load_data()

    # Create LogisticRegression Model
    model = LogisticRegression(
        solver='saga',
        random_state=utils.RANDOM_STATE,
        max_iter=10000,  # local epoch
        #  warm_start=True,  # prevent refreshing weights when fitting
    )

    # Setting initial parameters, akin to model.compile for keras models
    utils.set_initial_params(model)

    # Define Flower client
    class SyntheaClient(fl.client.NumPyClient):
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
            y_pred = model.predict(X_test)

            return loss, len(X_test), {"accuracy": accuracy, "balanced_accuracy": balanced_accuracy_score(y_test, y_pred), "f1_score": f1_score(y_test, y_pred, average='macro'), "mcc": matthews_corrcoef(y_test, y_pred)}

    # Start Flower client
    fl.client.start_numpy_client(SERVER_URL, client=SyntheaClient())
