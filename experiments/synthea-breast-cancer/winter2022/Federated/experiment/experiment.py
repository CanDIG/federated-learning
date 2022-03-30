# Adapted from https://github.com/adap/flower/tree/main/examples/sklearn-logreg-mnist

from typing import List, Dict, Any, Optional, Tuple, Union
from bases.base_experiment import Experiment
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from experiment.helpers.defaults import *
from experiment.helpers.parsers import *
from pandas.core.frame import DataFrame
from requests.models import Response
import pandas as pd
import numpy as np
import re
import os

# Constants
XY = Tuple[DataFrame, np.ndarray]
Dataset = Tuple[XY, XY]
LogRegParams = Union[XY, Tuple[np.ndarray]]

class FederatedLogReg(Experiment):
    """
    Implementation of Synthea Federated Logistic Regression Classifier
    """

    def __init__(
        self, 
        resource_url: Optional[str] = None, 
        random_state: Optional[int] = 1, 
        filename: Optional[str] = None, 
        client_number: Optional[str] = None,
        n_classes: Optional[int] = None,
        n_features: Optional[int] = None) -> None:

        self.filename = filename
        self.client_number = client_number
        self.table_id = self.__find_table_id()
        self.n_classes = n_classes
        self.n_features = n_features
        super().__init__(resource_url, random_state)

    def __find_table_id(self) -> Optional[str]:
        """
        Returns an optional string denoting the katsu db table_id for an optional client number, stored on a file called filename
        
        Returns:
            Optional[str]
        """

        with open(self.filename, "r") as f:
            tables = [table.strip("TABLE_UUID:").strip() for table in f.readlines()]
        
        if self.client_number is not None:
            return tables[int(self.client_number) - 1]
        
        return None
    
    def __create_dataframe(self, patients: List[Dict[str, Any]]) -> DataFrame:
        """
        Creates a Pandas Dataframe object from a List of Dictionaries containing the collected mCODE data

        Arguments:
            patients: List[Dict[str, Any]] containing patient information
        
        Returns:
            pd.Dataframe
        """
        
        df = pd.DataFrame(patients)
        df = df.dropna(subset=['numberOfMeds', 'nodes', 'primary', 'stage', 'sex', 'diagnosisAge', 'cancerStatus'])
        df = df.loc[df['sex'] != 0]
        df = df.loc[df['cancerType'] == 'Malignant neoplasm of breast (disorder)']
        df = df.drop(columns=['cancerType', 'sex'])
        return df.reset_index(drop=True)
    
    def __preprocess_mcode_req(self, req: Response) -> DataFrame:
        """
        Cleans Katsu-ingested + GraphQL served MCODE data and prepares for other preprocessing functions.

        Arguments:
            req: Response (raw response from GraphQL interface with provided query)

        Returns:
            pd.DataFrame
        """

        # Get JSON response
        patient_info_json = req.json().get('data').get('katsuDataModels').get('mcodeDataModels').get('mcodePackets')

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
        
        return self.__create_dataframe(patient_info_list)
    
    def __create_dataset_splits(self, df: DataFrame) -> Dataset:
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
            X.append([row.surgical, row.radiation, row.cancerStatus, row.diagnosisAge, row.primary, row.nodes, row.numberOfMeds])
            y.append(row.stage)
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state = self.RANDOM_STATE)
        return self.__scale_data(((X_train, y_train), (X_test, y_test)))
    
    def __undersample_majority_class(self, df: DataFrame) -> DataFrame:
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

        sample_size = min([len(stage_1), len(stage_2), len(stage_3), len(stage_4)])

        stage_1_new = stage_1.sample(n=sample_size, random_state=self.RANDOM_STATE)
        stage_2_new = stage_2.sample(n=sample_size, random_state=self.RANDOM_STATE)
        stage_3_new = stage_3.sample(n=sample_size, random_state=self.RANDOM_STATE)
        stage_4_new = stage_4.sample(n=sample_size, random_state=self.RANDOM_STATE)

        ml_sample = stage_2_new.append(stage_1_new)
        ml_sample = stage_3_new.append(ml_sample)
        ml_sample = stage_4_new.append(ml_sample)

        return ml_sample
    
    def __scale_data(self, data: Dataset) -> Dataset:
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
    
    def create_query(self) -> str:
        """
        Returns a str containing the GraphQL query for the specified table_id
        
        Returns:
            str
        """

        if self.table_id:
            return re.sub(r'TABLE_UUID', self.table_id, DEFAULT_QUERY)
        
        return re.sub(r'mcodePackets\(.*\)', "mcodePackets", DEFAULT_QUERY)
    
    def load_data(self) -> Dataset:
        """
        Queries the GraphQL-interface for all MCODE data and preprocesses it

        Returns:
            Dataset
        """

        # Get Client Number
        # client_num = os.getenv("FLOWER_CLIENT_NUMBER")
        
        # Get Query String
        query = self.create_query()

        # Request information from GraphQL
        data_json = self.send_graphql_request(query)

        # Apply preprocessing function
        preproc_df = self.__preprocess_mcode_req(data_json)

        # Split into train/test
        return self.__create_dataset_splits(self.__undersample_majority_class(preproc_df))
    
    def get_model_parameters(self, model: LogisticRegression) -> LogRegParams:
        if model.fit_intercept:
            return (model.coef_, model.intercept_)
        else:
            return (model.coef_,)
    
    def set_model_params(self, model: LogisticRegression, params: LogRegParams) -> LogisticRegression:
        model.coef_ = params[0]
        if model.fit_intercept:
            model.intercept_ = params[1]
        
        return model
    
    def set_initial_params(self, model: LogisticRegression) -> LogisticRegression:
        model.classes_ = np.array([i for i in range(self.n_classes)])
        model.coef_ = np.zeros((self.n_classes, self.n_features))

        if model.fit_intercept:
            model.intercept_ = np.zeros((self.n_classes))
        
        return model
        

experiment = FederatedLogReg(
    resource_url=os.getenv("GRAPHQL_INTERFACE_URL"),
    random_state=1729,
    filename=f"{os.getcwd()}/experiment/helpers/tables.txt",
    client_number=os.getenv("FLOWER_CLIENT_NUMBER"),
    n_classes=4,
    n_features=7
)