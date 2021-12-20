from typing import Tuple, Union, List
import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame
from pandas.core.series import Series
from requests.models import Response
from sklearn.linear_model import LogisticRegression
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
import requests
import json
import os
import datetime

RANDOM_STATE = 1729
XY = Tuple[pd.DataFrame, np.ndarray]
Dataset = Tuple[XY, XY]
LogRegParams = Union[XY, Tuple[np.ndarray]]
XYList = List[XY]

class DataFetchError(Exception):
    """"
    Exception raised for failing to fetch data.
        Attributes:
        message -- A message detailing the failing status code of the request
    """
    def __init__(self, message: str):
        self.message = message

def parse_diagnosis_age(row) -> float:
    """
    A function that returns the difference (in hours) between the diagnosis date and born date of a dataframe entry.
    
    Input: A (Katsu returned) JSON object of the MCODE data.
    Output: The difference between the diagnosis date and born date.
    """
    diag_date = row['cancerCondition'][0]['dateOfDiagnosis']
    diag_age = datetime.datetime(int(diag_date[0:4]), int(diag_date[5:7]), int(diag_date[8:10]))
    born_date = row['subject.dateOfBirth']
    born_age = datetime.datetime(int(born_date[0:4]), int(born_date[5:7]), int(born_date[8:10]))
    difference = diag_age - born_age
    diff_in_hrs = divmod(difference.total_seconds(), 3600)[0] # rounded down
    return diff_in_hrs

def load_data() -> Dataset:
    """Queries the GraphQL-interface for all MCODE data and preprocesses it.
    """
    def preprocess_mcode_req(req: Response) -> DataFrame:
        """
        Cleans Katsu-ingested + GraphQL served MCODE data and prepares for other preprocessing functions.
        See https://github.com/CanDIG/federated-learning/blob/main/examples/synthea-breast-cancer/Non-FederatedClassification.ipynb for
        brief justification of these steps.

        Arguments:
        req: req.Response (raw response from GraphQL interface with provided query)

        Returns:
        pd.DataFrame
        """
        # turn request into pandas Dataframe, dropping unnecessary columns and rows:
        all_results = json.loads(req.text)['data']['katsuDataModels']['mcodeDataModels']['mcodePackets']
        df = pd.json_normalize(all_results)
        for col in df:
            if df[col].astype(str).nunique() == 1:
                print(col)
                print(df[col].astype(str).unique()) # we drop null-valued and unnecessary columns.
                df = df.drop(col, axis=1)
        df = df.dropna(subset=['cancerDiseaseStatus.label']) # drop any rows that have empty disease status labels.

        # enumerate cancer_related_procedures into one-hot encoded columns
        all_procs = set()
        for _, row in df.iterrows():
            for i in row['cancerRelatedProcedures']:
                all_procs.add(i['code']['label'])
        dict_list_procs = []
        for _, row in df.iterrows():
            row_dict = dict.fromkeys(all_procs, 0)
            for i in row['cancerRelatedProcedures']:
                row_dict[i['code']['label']] += 1
            dict_list_procs.append(row_dict)
        df_procs = pd.DataFrame(dict_list_procs)

        # enumerate medication_statement into one-hot encoded columns
        all_meds = set()
        for _, row in df.iterrows():
            for i in row['medicationStatement']:
                all_meds.add(i['medicationCode']['label'])
                
        dict_list_meds = []
        for _, row in df.iterrows():
            row_dict = dict.fromkeys(all_meds, 0)
            for i in row['medicationStatement']:
                row_dict[i['medicationCode']['label']] += 1
            dict_list_meds.append(row_dict)
        df_meds = pd.DataFrame(dict_list_meds)

        # parse the age of diagnosis for each patient
        diag_age = df.apply(lambda row: parse_diagnosis_age(row), axis=1)
        diag_age_rename = diag_age.rename("diagnosisAge")
        df = df.join(pd.DataFrame(diag_age_rename))

        # drop cancer condition column (see Non-FederatedClassification.ipynb)
        df = df.drop(axis=1, labels=['cancerCondition', 'medicationStatement', 'cancerRelatedProcedures'])

        # concatenate all of the newly formatted columns together
        dfnew = pd.concat([df.reset_index(), df_procs, df_meds], axis=1, ignore_index=False)

        # one-hot encode the cancer_disease_status_label column, our dependent variable in this context.
        one_hot = pd.get_dummies(dfnew['cancerDiseaseStatus.label'])
        dfnew = dfnew.drop('cancerDiseaseStatus.label', axis=1)
        dfnew = dfnew.join(one_hot["Patient's condition improved"])

        # drop extraneous columns
        dfnew = dfnew.drop(['subject.dateOfBirth', 'index'], axis=1)

        return dfnew
    
    def undersample_majority_class(df: DataFrame) -> Tuple[DataFrame, Series]:
        """
        If this function is being used with the provided demo data ingested, then the positive class of
        "Patient's condition improved" will be massively overrepresented. To counter the effects of this
        on a logistic regression classifier, we massively undersample this majority class to be equal to 
        that of the negative class.

        Arguments:
        df: pd.DataFrame

        Returns:
        Tuple[pd.DataFrame, pd.Series]
        """
        positive_entries = df[df["Patient's condition improved"] == 1]
        positive_sample = positive_entries.sample(n=61, random_state=1729)

        negative_entries = df[df["Patient's condition improved"] == 0]

        ml_sample = positive_sample.append(negative_entries)
        X = ml_sample.drop("Patient's condition improved", axis=1)
        y = ml_sample["Patient's condition improved"]

        return (X, y)

    def pca_dimensionality_reduction(df: DataFrame) -> DataFrame:
        """
        If this function is being used with the provided demo data ingested, then there are 37 total
        features in the cleaned and preprocessed data. With only 122 examples, we use principal
        component analysis to drop this feature count to 10.

        Arguments:
        df: pd.DataFrame

        Returns:
        pd.DataFrame
        """
        pca = PCA(n_components=10, whiten=True)
        return pca.fit_transform(df)

    query = """
        query{
        katsuDataModels
        {
            mcodeDataModels
            {
            mcodePackets{
                subject {
                dateOfBirth
                sex
                }
                cancerCondition {
                dateOfDiagnosis
                }
                cancerRelatedProcedures {
                code {
                    label
                }
                }
                cancerDiseaseStatus {
                label
                }
                medicationStatement {
                medicationCode {
                    label
                }
                }
            }
            }
        }
        }
    """
    url = os.environ['GRAPHQL_INTERFACE_URL']
    req = requests.post(url, json={'query': query})
    if req.status_code != 200:
        raise DataFetchError(f"Could not query GraphQL interface, error code {req.status_code}")
    
    preproc_data = preprocess_mcode_req(req)
    X, y = undersample_majority_class(preproc_data)
    X = pca_dimensionality_reduction(X)
    # we do not split into validation sets due to low-volume of data
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE)

    return (x_train, y_train), (x_test, y_test)

def get_model_parameters(model: LogisticRegression) -> LogRegParams:
    """Returns the paramters of a sklearn LogisticRegression model."""
    if model.fit_intercept:
        params = (model.coef_, model.intercept_)
    else:
        params = (model.coef_,)
    return params


def set_model_params(
    model: LogisticRegression, params: LogRegParams
) -> LogisticRegression:
    """Sets the parameters of a sklean LogisticRegression model."""
    model.coef_ = params[0]
    if model.fit_intercept:
        model.intercept_ = params[1]
    return model


def set_initial_params(model: LogisticRegression):
    """Sets initial parameters as zeros Required since model params are
    uninitialized until model.fit is called.
    But server asks for initial parameters from clients at launch. Refer
    to sklearn.linear_model.LogisticRegression documentation for more
    information.
    """
    n_classes = 2  # We are training a binary classifier
    n_features = 10  # Number of features in dataset
    model.classes_ = np.array([i for i in range(n_classes)])
    model.coef_ = np.zeros((n_classes, n_features))
    if model.fit_intercept:
        model.intercept_ = np.zeros((n_classes,))

def shuffle(X: np.ndarray, y: np.ndarray) -> XY:
    """Shuffle X and y."""
    rng = np.random.default_rng(RANDOM_STATE)
    idx = rng.permutation(len(X))
    return X[idx], y[idx]


def partition(X: np.ndarray, y: np.ndarray, num_partitions: int) -> XYList:
    """Split X and y into a number of partitions."""
    return list(
        zip(np.array_split(X, num_partitions), np.array_split(y, num_partitions))
    )