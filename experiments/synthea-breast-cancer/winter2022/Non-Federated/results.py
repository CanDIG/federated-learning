'''results.py: File containing functions to print the results received'''

from sklearn.metrics import classification_report, confusion_matrix, balanced_accuracy_score
from sklearn.metrics import r2_score, f1_score, matthews_corrcoef
from sklearn.model_selection import cross_val_score
import pandas as pd

def print_results(y_test, y_pred):
    print('CONFUSION MATRIX:')
    print(confusion_matrix(y_test, y_pred))
    print()
    
    print('CLASSIFICATION REPORT:')
    print(classification_report(y_test, y_pred, zero_division=1, target_names=['Stage 1', 'Stage 2', 'Stage 3', 'Stage 4']))
    print()
    
    results_dict = {}
    results_dict['Balanced Accuracy'] = balanced_accuracy_score(y_test, y_pred)
    results_dict['Macro F1 Score'] = f1_score(y_test, y_pred, average='macro')
    results_dict['MCC'] = matthews_corrcoef(y_test, y_pred)
    results_df = pd.DataFrame([results_dict])
    
    print(results_df.to_string(index=False))

def print_cross_validation(model, X, y):
    print()
    print(f'AVERAGE CROSS-VALIDATION SCORE: {cross_val_score(model, X, y).mean()}')