# Adapted from https://github.com/adap/flower/tree/main/examples/sklearn-logreg-mnist

import flwr as fl
from experiment import experiment, model, eval_fn, Strategy, settings


def get_eval_fn():
    """Return an evaluation function for server-side evaluation."""
    _, (X_test, y_test) = experiment.load_data()
    return eval_fn(experiment, model, X_test, y_test)


# Start Flower server
if __name__ == "__main__":
    experiment.set_initial_params(model)
    strategy = Strategy(
        min_available_clients=settings.FL_MIN_CLIENTS,
        eval_fn=get_eval_fn(),
        on_fit_config_fn=lambda rnd: {"rnd": rnd}
    )

    server_url = f'{settings.FL_INTERNAL_HOST}:{settings.FL_INTERNAL_PORT}'
    fl.server.start_server(server_url, strategy=strategy, config={"num_rounds": settings.FL_ROUNDS})
    print(f"fl server started at {server_url}")
