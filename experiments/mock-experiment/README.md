# Mock Experiment
This directory details the creation of an experiment for use in federated machine learning. We use these experiments in conjunction with the fl-server and fl-client services to generate federated-learning experiments in a reusable manner. We use docker volumes to migrate the generated experiment to each of the docker containers. To implement such an intricate system, we follow a specific format, alongside the use of OOP principles like Abstraction to yield a reusable experiment structure.

## Directory Structure
```bash
mock-experiment
|__bases
   |  base_experiment.py
   |  base_flower_client.py
|__experiment
   |  __init__.py
   |  experiment.py
   |  flower_client.py
   |  get_eval_fn.py
   |  model.py
   |__helpers
      |  ... (extra files if necessary)
   |__checkpoints
      |  ... (model checkpoints saved)
```
Although the `mock-experiment` folder contains a `bases` subdirectory as well as an `experiment` subdirectory, for each experiment created, the `experiment` folder is the only directory that needs to be recreated as the `bases` directory will be added as a docker volume anyway.

### Bases Directory
This directory houses the abstract base classes for the Experiment and FlowerClient types. These abstract base classes are overridden for each experiment to enable custom experiments, while also having a common base by which the client.py and server.py files can call the required functions.

**Experiment** 
> Abstract Base Class used for creating federated-learning experiments.
> - Defines a method named `create_query` to generate GraphQL queries
>   - Returns a string containg the well-formed GraphQL query.
> - Defines a method named `load_data` to load data for experiment.
>   - Returns a Tuple of Tuples containg the training and testing data in the following form: `(X_train, y_train), (X_test, y_test)`, where all data prefaced by `X_` are `pd.DataFrame` objects and data prefaced by `y_` are `np.ndarray` objects.
> - Defines a method named `get_model_parameters` to return model parameters.
>   - The data should be returned as a tuple, such that the order of the params is identical to the order in `set_model_params` and `set_initial_params`.
> - Defines a method named `set_model_params` to return a model with the updated parameters.
>   - Returns a model object after updating its parameters.
> - Defines a method named `set_initial_params` to return a model with the initial parameters.
>   - Returns a model object after setting its initial parameters.
> - Implements a method named `send_graphql_request` to return the response from a query to the graphql interface
>   - Takes in a fully-formed graphql query and returns a Response object.
> A child class must override at least the first 6 methods.

**BaseFlowerClient**
> Abstract Base Class used to evaluate and fit the model.
> - Defines a method named `get_parameters` to return model parameters.
>   - The format of the parameters will most likely be a Tuple, in the same order as used in the **Experiment** methods.
> - Defines a method named `fit` to fit the model based on the data collected and to return the parameters of the model after fitting.
>   - Parameters are passed in the same format as specified above, and the model parameters, length of training set and extra properties are returned.
> - Defines a method named `evaluate` to evaluate the performance of a model and to return its evaluation metrics.
>   - Parameters are passed like above, though the return is only a loss quantity associated with the model, as well as any extra evaluation metrics determined. 
> A child class must override all three of the methods listed above.

### Experiment Directory
This directory houses the child classes as well as helper files to enable the experiment to be used in the fl-services. This directory is added via docker volumes to each fl-client and fl-server to allow the experiment to be conducted.

**\_\_init\_\_.py**
> Defines modules that can be imported from the `experiment` folder. There must be exactly four of these values, and they must be named exactly as follows.
> - *experiment*: An instance of the child class that inherited from the `Experiment` base class. This instance has its parameters initialized in the `experiment.py` file.
> - *model*: An instance of the model that one wishes to federate. This instance has its parameters initialized in the `model.py` file.
> - *FlowerClient*: A child class of the `BaseFlowerClient`.
> - *eval_fn*: A function used to generate an evaluation function for the federated-learning models.

**experiment.py**
> Defines a child class of the `Experiment` abstract base class. This child class overrides at least the six required abstract methods. An instance of the new subclass named `experiment` is generated with the required parameters, at the end of the file.

**flower_client.py**
> Defines a child class, `FlowerClient` of the `BaseFlowerClient` abstract base class. The child class overrides the three required abstract methods. 

**get_eval_fn.py**
> Defines a function generating function called `eval_fn` that takes in an `Experiment` object, a model, as well as the X and y data for the testing set. A function that takes in a `flwr.common.Weights` parameter is returned. This function returns a tuple containing the loss of the model and a dictiontionary with extra evaluation metrics. It should be similar in nature to the **flower_client.py** evaluate function.

**model.py**
> Defines an instance of the model to federate, with its required parameters. 

## fl-server
The fl-server by itself has no extraneous code dedicated to any specific experiment. Instead, using the quickstart script, docker volumes are added to ensure that the `bases` and an `experiment` folder are added to the container. To ensure compatibility with all experiments, the `server.py` file imports the `experiment`, `model` & `eval_fn` values from the `experiment` folder. Given what was talked about above, we know that these values will change depending upon the specific experiment at hand. This is why the structure and naming of the functions must remain consistent.

## fl-client
The fl-client also doesn't have any experiment-specific code. Instead, it also imports modules from the `experiment` folder, which is added as a docker volume. The rigid naming conventions are once again put in place to ensure that the client file works without major revisions from one experiment to the next.

## Generating an experiment
To make your own experiment, you have to create an experiment folder like the one in this subdirectory, or like the [synthea experiments folder](../synthea-breast-cancer/winter2022/Federated/experiment). Place this experiment folder inside your own experiment subdirectory within the larger `experiments` root subdirectory (eg. `experiments/my-new-experiment/experiment/`). Ensure that you have at least the 5 files present in the example folder, within your new folder. Don't change the names or parameters of the items that will be imported through the \_\_init\_\_.py file (eg. `experiment`, `model`, `FlowerClient` & `eval_fn`), but feel free to change the names of other items (eg. `MockExperiment`) - Just ensure you have made the changes to the name in all places required. If you have any extra files you want to add to the experiment, create a subdirectory within the `experiment` folder called `helpers`, that houses any such functions. An example of this can be found within the [synthea experiments folder](../synthea-breast-cancer/winter2022/Federated/experiment).