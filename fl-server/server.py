# Adapted from https://github.com/adap/flower/tree/main/examples/sklearn-logreg-mnist

import flwr as fl
import numpy as np
import utils
from sklearn.metrics import log_loss
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from typing import Dict, List, Optional, Tuple


def fit_round(rnd: int) -> Dict:
    """Send round number to client."""
    return {"rnd": rnd}


def get_eval_fn(model: LogisticRegression):
    """Return an evaluation function for server-side evaluation."""

    print("getting test data")
    # Load test data here to avoid the overhead of doing it in `evaluate` itself
    _, (X_test, y_test) = utils.load_data()

    # The `evaluate` function will be called after every round
    def evaluate(parameters: fl.common.Weights):
        # Update model with the latest parameters
        utils.set_model_params(model, parameters)
        loss = log_loss(y_test, model.predict_proba(X_test))
        accuracy = model.score(X_test, y_test)
        auc_score = roc_auc_score(y_test, model.predict(X_test))
        print(f"auc score: {auc_score}")

        return loss, {"accuracy": accuracy, "auc score": auc_score}

    return evaluate

# Create a custom Flower Strategy class to save model checkpoints (this will save inside the fl-server Docker container)
class SaveModelStrategy(fl.server.strategy.FedAvg):
    """
    Adapted from https://flower.dev/docs/saving-progress.html.
    Saves aggregated weights to a .npz file every 10 rounds of learning.
    Proceeds normally as per Federated Averaging otherwise.
    """
    def aggregate_fit(
        self,
        rnd: int,
        results: List[Tuple[fl.server.client_proxy.ClientProxy, fl.common.FitRes]],
        failures: List[BaseException],
    ) -> Optional[fl.common.Weights]:
        aggregated_weights = super().aggregate_fit(rnd, results, failures)
        if aggregated_weights is not None and rnd % 10 == 0:
            # Save aggregated_weights
            print(f"Saving round {rnd} aggregated_weights...")
            np.savez(f"round-{rnd}-weights.npz", *aggregated_weights)
        return aggregated_weights



# Start Flower server for five rounds of federated learning
if __name__ == "__main__":
    model = LogisticRegression()
    utils.set_initial_params(model)
    strategy = SaveModelStrategy(
        min_available_clients=2,
        eval_fn=get_eval_fn(model),
        on_fit_config_fn=fit_round,
    )
    fl.server.start_server("0.0.0.0:8080", strategy=strategy, config={"num_rounds": 100})
    print("fl server started at 0.0.0.0:8080")
