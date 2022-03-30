# Adapted from https://github.com/adap/flower/tree/main/examples/sklearn-logreg-mnist
import os
import flwr as fl
import numpy as np
from typing import Dict, List, Optional, Tuple
from experiment import experiment, model, eval_fn, settings

CHECKPOINT_PATH = 'experiment/checkpoints'

def fit_round(rnd: int) -> Dict:
    """Send round number to client."""
    return {"rnd": rnd}


def get_eval_fn():
    """Return an evaluation function for server-side evaluation."""
    _, (X_test, y_test) = experiment.load_data()
    return eval_fn(experiment, model, X_test, y_test)

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

        if not os.path.exists(CHECKPOINT_PATH):
            os.makedirs(CHECKPOINT_PATH)

        if aggregated_weights is not None and rnd % 10 == 0:
            # Save aggregated_weights
            print(f"Saving round {rnd} aggregated_weights...")
            np.savez(f"{CHECKPOINT_PATH}/round-{rnd}-weights.npz", *aggregated_weights)
        
        return aggregated_weights



# Start Flower server for five rounds of federated learning
if __name__ == "__main__":
    experiment.set_initial_params(model)
    strategy = SaveModelStrategy(
        min_available_clients=settings.FL_MIN_CLIENTS,
        eval_fn=get_eval_fn(),
        on_fit_config_fn=fit_round,
    )

    server_url = f'{settings.FL_INTERNAL_HOST}:{settings.FL_INTERNAL_PORT}'
    fl.server.start_server(server_url, strategy=strategy, config={"num_rounds": settings.FL_ROUNDS})
    print(f"fl server started at {server_url}")
