from sklearn.metrics import log_loss, balanced_accuracy_score, f1_score, matthews_corrcoef
from sklearn.linear_model import LogisticRegression
from experiment.experiment import FederatedLogReg
import pandas as pd
import flwr as fl

def eval_fn(experiment: FederatedLogReg, model: LogisticRegression, X_test, y_test):
    def evaluate(parameters: fl.common.Weights):
        new_model = experiment.set_model_params(model, parameters)
        loss = log_loss(y_test, new_model.predict_proba(X_test))
        accuracy = new_model.score(X_test, y_test)
        y_pred = new_model.predict(X_test)

        results_dict = {}
        results_dict['Balanced Accuracy'] = balanced_accuracy_score(y_test, y_pred)
        results_dict['Macro F1 Score'] = f1_score(y_test, y_pred, average='macro')
        results_dict['MCC'] = matthews_corrcoef(y_test, y_pred)
        results_df = pd.DataFrame([results_dict])

        print(f"Accuracy: {accuracy}")
        print(results_df.to_string(index=False))

        return loss, {"accuracy": accuracy, "balanced_accuracy": results_dict['Balanced Accuracy'], "f1_score": results_dict['Macro F1 Score'], "mcc": results_dict['MCC']}
    
    return evaluate