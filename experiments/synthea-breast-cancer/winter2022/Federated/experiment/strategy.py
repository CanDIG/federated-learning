import os
import flwr
import numpy as np
import experiment.settings
from typing import List, Optional, Tuple

class Strategy(flwr.server.strategy.FedAvg):
    """
    Adapted from https://flower.dev/docs/saving-progress.html.
    Saves aggregated weights to a .npz file every 10 rounds of learning.
    Proceeds normally as per Federated Averaging otherwise.
    """

    def aggregate_fit(
        self,
        rnd: int,
        results: List[Tuple[flwr.server.client_proxy.ClientProxy, flwr.common.FitRes]],
        failures: List[BaseException],
    ) -> Optional[flwr.common.Weights]:
        aggregated_weights = super().aggregate_fit(rnd, results, failures)

        if not os.path.exists(experiment.settings.FL_CHECKPOINT_PATH):
            os.makedirs(experiment.settings.FL_CHECKPOINT_PATH)

        if aggregated_weights is not None and rnd % 10 == 0:
            # Save aggregated_weights
            print(f"Saving round {rnd} aggregated_weights...")
            np.savez(f"{experiment.settings.FL_CHECKPOINT_PATH}/round-{rnd}-weights.npz", *aggregated_weights)
        
        return aggregated_weights