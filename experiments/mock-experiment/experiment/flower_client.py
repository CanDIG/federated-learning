from bases.base_flower_client import BaseFlowerClient

class FlowerClient(BaseFlowerClient):
    def get_parameters(self):
        return self.experiment.get_model_parameters(self.fl_model)
    
    def fit(self, parameters, config):
        self.fl_model = self.experiment.set_model_params(self.fl_model, parameters)
        self.fl_model.fit(self.dataset[0][0], self.dataset[1][0])
        return self.experiment.get_model_parameters(self.fl_model), len(self.dataset[0][0]), {}
    
    def evaluate(self, parameters, config):
        return "loss, len(self.dataset[1][0]), {}"