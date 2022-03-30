from experiment.experiment import MockExperiment
import flwr as fl

def eval_fn(experiment: MockExperiment, model, X_test, y_test):
    def evaluate(parameters: fl.common.Weights):
        """
        Return a tuple containing a loss quantity as its first parameter and a dictionary containing evaluation metric scores as its second paramter 
        """
        return "loss, {}"
    
    return evaluate