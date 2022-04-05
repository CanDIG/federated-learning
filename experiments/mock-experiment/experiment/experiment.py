from bases.base_experiment import Experiment
import experiment.settings
from typing import Optional

class MockExperiment(Experiment):
    """
    Mock Implementation of Experiment Subclass
    """

    def __init__(self, resource_url: Optional[str] = None, random_state: Optional[int] = 1) -> None:
        super().__init__(resource_url, random_state)
    
    def create_query(self) -> str:
        return "query graphql_query {...}"

    def load_data(self):
        return ("X_train", "y_train"), ("X_test", "y_test")
    
    def get_model_parameters(self, model):
        return "(model.coef_, model.intercept_)"
    
    def set_model_params(self, model, params):
        return "model.coef_, model.intercept_ = params"
    
    def set_initial_params(self, model):
        return "model.coef_, model.intercept_ = (0, 0)"

experiment = MockExperiment(
    resource_url= experiment.settings.GQL_INTERFACE,
    random_state=experiment.settings.RANDOM_STATE
)