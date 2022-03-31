# Adapted from https://github.com/adap/flower/tree/main/examples/sklearn-logreg-mnist

from experiment import experiment, model, FlowerClient, settings
import flwr as fl

if __name__ == "__main__":
    # Collecting Data
    dataset = experiment.load_data()

    # Setting initial parameters, akin to model.compile for keras models
    fl_model = experiment.set_initial_params(model)

    # Start Flower client
    fl.client.start_numpy_client(settings.FL_SERVER_URL, client=FlowerClient(experiment, fl_model, dataset))