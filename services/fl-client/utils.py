# Adapted from https://github.com/adap/flower/tree/main/examples/sklearn-logreg-mnist

# Imports - Helpers
from helpers.parsers import PatientInfoParser, UniqueInfoParser
from helpers.defaults import *

# Imports - Processing
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from pandas.core.frame import DataFrame
import numpy as np
import pandas as pd

# Imports - Typing
from typing import List, Dict, Any, Tuple, Union

# Imports - Requests
from requests.models import Response
import requests
import os


# Constants
RANDOM_STATE = 1729
XY = Tuple[pd.DataFrame, np.ndarray]

# Types
Dataset = Tuple[XY, XY]
LogRegParams = Union[XY, Tuple[np.ndarray]]
XYList = List[XY]

# Error Class


class DataFetchError(Exception):
    """"
    Exception raised for failing to fetch data.
        Attributes:
        message -- A message detailing the failing status code of the request
    """

    def __init__(self, message: str):
        self.message = message


def load_data() -> Dataset:
    """Queries the GraphQL-interface for all MCODE data and preprocesses it.
    """

    def get_request(query: str) -> Response:
        """
        Returns a Response object for a GraphQL query that is passed in

        Arguments:
            query: str containing GraphQL formatted query

        Returns:
            Response
        """

        graphql_url = os.getenv("GRAPHQL_INTERFACE_URL", None)

        if graphql_url is None:
            raise DataFetchError(f"No GraphQL interface URL specified")

        request = requests.post(graphql_url, json={"query": query})
        if request.status_code != 200:
            raise DataFetchError(
                f"Could not query GraphQL interface. Error code: {request.status_code}")

        return request

    def create_dataframe(patients: List[Dict[str, Any]]) -> DataFrame:
        """
        Creates a Pandas Dataframe object from a List of Dictionaries containing the collected mCODE data

        Arguments:
            patients: List[Dict[str, Any]] containing patient information

        Returns:
            pd.Dataframe
        """

        df = pd.DataFrame(patients)
        df = df.dropna(subset=['numberOfMeds', 'nodes', 'primary',
                       'stage', 'sex', 'diagnosisAge', 'cancerStatus'])
        df = df.loc[df['sex'] != 0]
        df = df.loc[df['cancerType'] ==
                    'Malignant neoplasm of breast (disorder)']
        df = df.drop(columns=['cancerType', 'sex'])
        return df.reset_index(drop=True)

    def preprocess_mcode_req(req: Response) -> DataFrame:
        """
        Cleans Katsu-ingested + GraphQL served MCODE data and prepares for other preprocessing functions.

        Arguments:
            req: Response (raw response from GraphQL interface with provided query)

        Returns:
            pd.DataFrame
        """

        # Get JSON response
        patient_info_json = req.json().get('data').get(
            'katsuDataModels').get('mcodeDataModels').get('mcodePackets')

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

        return create_dataframe(patient_info_list)

    def create_dataset_splits(df: DataFrame) -> Dataset:
        """
        Split data into training and testing sets from passed in DataFrame, in the form of a tuple of tuples, ((X,Y),(X,Y))

        Arguments: 
            df: DataFrame containing full Dataset

        Response:
            Dataset object
        """

        # Split into X and y
        X = []
        y = []

        for _, row in df.iterrows():
            X.append([row.surgical, row.radiation, row.cancerStatus,
                     row.diagnosisAge, row.primary, row.nodes, row.numberOfMeds])
            y.append(row.stage)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=RANDOM_STATE)
        return scale_data(((X_train, y_train), (X_test, y_test)))

    def undersample_majority_class(df: DataFrame) -> DataFrame:
        """
        If this function is being used with the provided demo data ingested, then will be an overrepresentation of stage 2 and 3. 
        To counter the effects of this
        on a logistic regression classifier, we massively undersample this majority classes to be equal to that of the minority class.

        Arguments:
        df: pd.DataFrame

        Returns:
        Tuple[pd.DataFrame, pd.Series]
        """
        stage_1 = df[df["stage"] == 1]
        stage_2 = df[df["stage"] == 2]
        stage_3 = df[df["stage"] == 3]
        stage_4 = df[df["stage"] == 4]

        sample_size = min([len(stage_1), len(stage_2),
                          len(stage_3), len(stage_4)])

        stage_1_new = stage_1.sample(n=sample_size, random_state=RANDOM_STATE)
        stage_2_new = stage_2.sample(n=sample_size, random_state=RANDOM_STATE)
        stage_3_new = stage_3.sample(n=sample_size, random_state=RANDOM_STATE)
        stage_4_new = stage_4.sample(n=sample_size, random_state=RANDOM_STATE)

        ml_sample = pd.concat(
            [stage_4_new, stage_3_new, stage_2_new, stage_1_new])

        return ml_sample

    def scale_data(data: Dataset) -> Dataset:
        """
        Scale input data using sklearn StandardScaler to prepare for testing

        Arguments:
            data: Dataset object containing training and testing data

        Returns:
            Dataset
        """

        scaler = StandardScaler()

        training_set = data[0]
        testing_set = data[1]

        X_train = training_set[0]
        y_train = training_set[1]
        X_test = testing_set[0]
        y_test = testing_set[1]

        scaler.fit(X_train)
        X_train = scaler.transform(X_train)
        X_test = scaler.transform(X_test)

        return (X_train, y_train), (X_test, y_test)

    # Request information from GraphQL
    data_json = get_request(DEFAULT_QUERY)

    # Apply preprocessing function
    preproc_df = preprocess_mcode_req(data_json)

    # Split into train/test
    return create_dataset_splits(undersample_majority_class(preproc_df))


def get_model_parameters(model: LogisticRegression) -> LogRegParams:
    """
    Returns the paramters of a sklearn LogisticRegression model.

    Arguments:
        model: LogisticRegression model whose params are needed 

    Returns:
        LogRegParams
    """

    if model.fit_intercept:
        params = (model.coef_, model.intercept_)
    else:
        params = (model.coef_,)
    return params


def set_model_params(model: LogisticRegression, params: LogRegParams) -> LogisticRegression:
    """
    Sets the parameters of a sklean LogisticRegression model.

    Arguments:
        model: LogisticRegression model
        params: LogRegParams to implement in the model

    Returns:
        LogisticRegression
    """

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

    n_classes = 4
    n_features = 7
    model.classes_ = np.array([i for i in range(n_classes)])
    model.coef_ = np.zeros((n_classes, n_features))
    if model.fit_intercept:
        model.intercept_ = np.zeros((n_classes,))
