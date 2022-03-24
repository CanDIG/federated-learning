# Adapted from https://github.com/adap/flower/tree/main/examples/sklearn-logreg-mnist

from typing import List, Optional, Dict, Any, Tuple, Union
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
import re
import requests
from helpers.defaults import *
from helpers.parsers import PatientInfoParser, UniqueInfoParser


dataset_graphql_url = 'http://localhost:5003'

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
    diag_age = datetime.datetime(int(diag_date[0:4]), int(
        diag_date[5:7]), int(diag_date[8:10]))
    born_date = row['subject.dateOfBirth']
    born_age = datetime.datetime(int(born_date[0:4]), int(
        born_date[5:7]), int(born_date[8:10]))
    difference = diag_age - born_age
    diff_in_hrs = divmod(difference.total_seconds(), 3600)[0]  # rounded down
    return diff_in_hrs


def load_data() -> Dataset:
    """Queries the GraphQL-interface for all MCODE data and preprocesses it.
    """
    def preprocess_mcode_req(req: Response) -> DataFrame:
        """
        Cleans Katsu-ingested + GraphQL served MCODE data and prepares for other preprocessing functions.

        Arguments:
        req: req.Response (raw response from GraphQL interface with provided query)

        Returns:
        pd.DataFrame
        """
        # Defines unique medications and procedure types
        uniq_finder = UniqueInfoParser(patient_info_json)
        uniq_meds = uniq_finder.get_uniq_meds()
        uniq_procedures = uniq_finder.get_uniq_procedures()

        # Create list of patient info
        patient_info_list = []
        for patient in patient_info_json:
            patient_info_dict = {}
            patient_info = PatientInfoParser(
                uniq_meds, uniq_procedures, patient).get_patient_data()

            number_of_meds = sum(
                [quantity for quantity in patient_info.meds.values()])

            for procedure in uniq_procedures:
                patient_info_dict[procedure] = patient_info.procedures[procedure]

            patient_info_dict['sex'] = patient_info.sex
            patient_info_dict['nodes'] = patient_info.nodes
            patient_info_dict['stage'] = patient_info.stage
            patient_info_dict['numberOfMeds'] = number_of_meds
            patient_info_dict['primary'] = patient_info.primary
            patient_info_dict['diagnosisAge'] = patient_info.age
            patient_info_dict['cancerType'] = patient_info.cancer_type
            patient_info_dict['cancerStatus'] = patient_info.cancer_status
            patient_info_list.append(patient_info_dict)

        # Clean up and create dataset
        pd.set_option('display.max_columns', None)
        df = pd.DataFrame(patient_info_list)
        df = df.dropna(subset=['numberOfMeds', 'nodes', 'primary',
                       'stage', 'sex', 'diagnosisAge', 'cancerStatus'])
        df = df.loc[df['sex'] != 0]
        df = df.loc[df['cancerType'] ==
                    'Malignant neoplasm of breast (disorder)']
        df = df.drop(columns=['cancerType', 'sex'])
        df = df.reset_index(drop=True)
        return df

    # Request information from GraphQL
    data_json = requests.post(dataset_graphql_url, json={
                              'query': DEFAULT_QUERY})
    if data_json.status_code != 200:
        raise DataFetchError(
            f"Could not query GraphQL interface, error code {data_json.status_code}")

    patient_info_json = data_json.json().get('data').get(
        'katsuDataModels').get('mcodeDataModels').get('mcodePackets')

    # Apply preprocessing function
    preproc_df = preprocess_mcode_req(data_json)

    # Split into X and y
    X = []
    y = []

    for index, row in preproc_df.iterrows():
        X.append([row.surgical, row.radiation, row.cancerStatus,
                 row.diagnosisAge, row.primary, row.nodes, row.numberOfMeds])
        y.append(row.stage)

    # Split into train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=1729)

    return (X_train, y_train), (X_test, y_test)


def get_model_parameters(model: LogisticRegression) -> LogRegParams:
    """Returns the paramters of a sklearn LogisticRegression model."""
    if model.fit_intercept:
        params = (model.coef_, model.intercept_)
    else:
        params = (model.coef_,)
    return params


def set_model_params(model: LogisticRegression, params: LogRegParams) -> LogisticRegression:
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
        zip(np.array_split(X, num_partitions),
            np.array_split(y, num_partitions))
    )
