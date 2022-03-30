from requests.models import Response
from abc import ABC, abstractmethod
from typing import Optional
import requests

class DataFetchError(Exception):
    """"
    Exception raised for failing to fetch data.
        Attributes:
        message -- A message detailing the failing status code of the request
    """

    def __init__(self, message: str):
        self.message = message

class Experiment(ABC):
    """
    Abstract Base Class used for creating federated-learning experiments
    """
    
    def __init__(self, resource_url: Optional[str] = None, random_state: Optional[int] = 1) -> None:
        self.resource_url = resource_url
        self.RANDOM_STATE = random_state
        super().__init__()
    
    @abstractmethod
    def create_query(self) -> str:
        """
        Return a GraphQL query string with which to query the GraphQL interface for data. Return an empty string if not using GraphQL.
        """
        pass
    
    @abstractmethod
    def load_data(self):
        """
        Return a Tuple of 2 Tuples, the first sub-tuple containing the X and y training data, and the second containing the X and y testing data. The X data must be in a pd.DataFrame, whereas the y data must be a np.ndarray object.
        """
        pass

    @abstractmethod
    def get_model_parameters(self, model):
        """
        Return the parameters of the model you are using as a tuple. Ensure that the model parameters are being extracted in a similar fashion to how they are set in set_model_params.
        """
        pass

    @abstractmethod
    def set_model_params(self, model, params):
        """
        Set a model with the passed in parameters, and return said model back to the client.
        """
        pass

    @abstractmethod
    def set_initial_params(self, model):
        """
        Set a model's initial parameters and then return it back to the client.
        """
        pass

    def send_graphql_request(self, query: str) -> Response:
        """
        Send a GraphQL query with a properly formatted GraphQL query string and return a Response object containing the collected response.
        """
        
        if self.resource_url is None:
            raise DataFetchError(f"No URL specified")

        request = requests.post(self.resource_url, json={"query": query})
        if request.status_code != 200:
            raise DataFetchError(f"Could not query GraphQL. Error code: {request.status_code}")
        
        return request