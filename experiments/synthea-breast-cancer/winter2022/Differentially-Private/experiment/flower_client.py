from sklearn.metrics import log_loss, balanced_accuracy_score, f1_score, matthews_corrcoef
from bases.base_flower_client import BaseFlowerClient
from sklearn.linear_model import LogisticRegression
from experiment.experiment import FederatedLogReg
import warnings

class FlowerClient(BaseFlowerClient):
    def __init__(self, experiment: FederatedLogReg, fl_model: LogisticRegression, dataset) -> None:
        self.X_train = dataset[0][0]
        self.y_train = dataset[0][1]
        self.X_test = dataset[1][0]
        self.y_test = dataset[1][1]
        super().__init__(experiment, fl_model, dataset)

    def get_parameters(self):
        return self.experiment.get_model_parameters(self.fl_model)

    def fit(self, parameters, config):
        self.fl_model = self.experiment.set_model_params(self.fl_model, parameters)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.fl_model.fit(self.X_train, self.y_train)
        
        print(f"Training finished for round {config['rnd']}")
        return self.experiment.get_model_parameters(self.fl_model), len(self.X_train), {}

    def evaluate(self, parameters, config):
        self.fl_model = self.experiment.set_model_params(self.fl_model, parameters)
        loss = log_loss(self.y_test, self.fl_model.predict_proba(self.X_test))
        accuracy = self.fl_model.score(self.X_test, self.y_test)
        y_pred = self.fl_model.predict(self.X_test)

        return loss, len(self.X_test), {"accuracy": accuracy, "balanced_accuracy": balanced_accuracy_score(self.y_test, y_pred), "f1_score": f1_score(self.y_test, y_pred, average='macro'), "mcc": matthews_corrcoef(self.y_test, y_pred)}