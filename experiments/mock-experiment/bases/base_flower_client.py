from abc import ABC, abstractmethod
import flwr as fl

class BaseFlowerClient(fl.client.NumPyClient, ABC):
    def __init__(self, experiment, fl_model, dataset) -> None:
        self.experiment = experiment
        self.fl_model = fl_model
        self.dataset = dataset
        super().__init__()

    @abstractmethod
    def get_parameters(self):
        """
        Returns the parameters used for the current model
        """
        pass

    @abstractmethod
    def fit(self, parameters, config):
        """
        Fit the model based on the data collected, and return the parameters, length of the training dataset and extra properties
        """
        pass

    @abstractmethod
    def evaluate(self, parameters, config):
        """
        Evaluate the model based on several criteria like loss. Return a tuple containing the loss, length of the test dataset and any extra evaluation metrics, stored in a dictionary
        """
        pass