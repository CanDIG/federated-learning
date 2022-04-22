# Experiment Structure
The `experiments/mock-experiment` directory details the creation of an experiment for use in federated machine learning. We use these experiments in conjunction with the fl-server and fl-client services to generate federated-learning experiments in a reusable manner. We use docker volumes to migrate the generated experiment to each of the docker containers. To implement such an intricate system, we follow a specific format, alongside the use of OOP principles like Abstraction to yield a reusable experiment structure.

## Mock-Experiment Structure
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
  |  settings.py
  |  strategy.py
  |  experiment-requirements.txt
  |__helpers
     |  ... (extra files if necessary)
  |__checkpoints
     |  ... (model checkpoints saved)
```
Although the `mock-experiment` folder contains a `bases` subdirectory as well as an `experiment` subdirectory, for each experiment created, the `experiment` folder is the only directory that needs to be recreated as the `bases` directory will be added as a docker volume anyway. This new `experiment` folder can be modeled after the [synthea experiments folder](../experiments/synthea-breast-cancer/winter2022/Federated/experiment) (more details in [generating an experiment](#generating-an-experiment)).

### Bases Directory
This directory houses the abstract base classes for the Experiment and FlowerClient types. These abstract base classes are overridden for each experiment to enable custom experiments, while also having a common base by which the client.py and server.py files can call the required functions.

#### base_experiment.py 
Abstract Base Class, **Experiment**, used for creating federated-learning experiments.
- Defines a method named `create_query` to generate GraphQL queries
  - Returns a string containing the well-formed GraphQL query.
- Defines a method named `load_data` to load data for experiment.
  - Returns a Tuple of Tuples containing the training and testing data in the following form: `(X_train, y_train), (X_test, y_test)`, where all data prefaced by `X_` are `pd.DataFrame` objects and data prefaced by `y_` are `np.ndarray` objects.
- Defines a method named `get_model_parameters` to return model parameters.
  - The data should be returned as a tuple, such that the order of the params is identical to the order in `set_model_params` and `set_initial_params`.
- Defines a method named `set_model_params` to return a model with the updated parameters.
  - Returns a model object after updating its parameters.
- Defines a method named `set_initial_params` to return a model with the initial parameters.
  - Returns a model object after setting its initial parameters.
- Implements a method named `send_graphql_request` to return the response from a query to the graphql interface
  - Takes in a fully-formed graphql query and returns a Response object. 
- A child class must override at least the first 6 methods.

#### base_flower_client.py
Abstract Base Class, **BaseFlowerClient** used to evaluate and fit the model.
- Defines a method named `get_parameters` to return model parameters.
  - The format of the parameters will most likely be a Tuple, in the same order as used in the **Experiment** methods.
- Defines a method named `fit` to fit the model based on the data collected and to return the parameters of the model after fitting.
  - Parameters are passed in the same format as specified above, and the model parameters, length of training set and extra properties are returned.
- Defines a method named `evaluate` to evaluate the performance of a model and to return its evaluation metrics.
  - Parameters are passed like above, though the return is only a loss quantity associated with the model, as well as any extra evaluation metrics determined. 
- A child class must override all three of the methods listed above.

### Experiment Directory
This directory houses the child classes as well as helper files to enable the experiment to be used in the fl-services. This directory is added via docker volumes to each fl-client and fl-server to allow the experiment to be conducted.

#### \_\_init\_\_.py
Defines modules that can be imported from the `experiment` folder. There must be exactly five of these values, and they must be named exactly as follows.
- *experiment*: An instance of the child class that inherited from the `Experiment` base class. This instance has its parameters initialized in the `experiment.py` file.
- *model*: An instance of the model that one wishes to federate. This instance has its parameters initialized in the `model.py` file.
- *FlowerClient*: A child class of the `BaseFlowerClient`.
- *eval_fn*: A function used to generate an evaluation function for the federated-learning models.
- *settings*: A file named `settings.py` containing constants and experiment parameters for the fl-* services.

#### experiment.py
Defines a child class of the `Experiment` abstract base class. This child class overrides at least the six required abstract methods. An instance of the new subclass named `experiment` is generated with the required parameters, at the end of the file.

#### flower_client.py
Defines a child class, `FlowerClient` of the `BaseFlowerClient` abstract base class. The child class overrides the three required abstract methods. 

#### get_eval_fn.py
Defines a function generating function called `eval_fn` that takes in an `Experiment` object, a model, as well as the X and y data for the testing set. A function that takes in a `flwr.common.Weights` parameter is returned. This function returns a tuple containing the loss of the model and a dictionary with extra evaluation metrics. It should be similar in nature to the **flower_client.py** evaluate function.

#### model.py
Defines an instance of the model to federate, with its required parameters. 

#### settings.py
Defines constants for use in the fl-* services.

#### strategy.py
Defines a child class `Strategy`, that will override the `flwr.server.strategy.FedAvg` class, or one of its derivatives, like `flwr.server.strategy.QFedAvg`. If you wish to use one of the existing flower strategies, define a child class called `Strategy` that inherits from the strategy of your choice, like below:

```python
class Strategy(flwr.server.strategy.FedAvg):
    pass
```

#### experiment-requirements.txt
Defines additional python modules that are required, beyond the ones present in the fl-server's and the fl-client's experiment-requirements.txt files. It is recommended that you specify each required module in the form `[module]==[version]` to ensure that your experiment will work in the future. The fl-server and fl-client base requirements are not labeled as such because we wish for them to update continually. This file is essential since the Dockerfile won't complete without this file. If you have no additional dependencies, leave the `experiment-requirements.txt` file empty.

## fl-server
The fl-server by itself has no extraneous code dedicated to any specific experiment. Instead, using the quickstart script, docker volumes are added to ensure that the `bases` and an `experiment` folder are added to the container. To ensure compatibility with all experiments, the `server.py` file imports the `experiment`, `model` & `eval_fn` values from the `experiment` folder. Given what was talked about above, we know that these values will change depending upon the specific experiment at hand. This is why the structure and naming of the functions must remain consistent.

## fl-client
The fl-client also doesn't have any experiment-specific code. Instead, it also imports modules from the `experiment` folder, which is added as a docker volume. The rigid naming conventions are once again put in place to ensure that the client file works without major revisions from one experiment to the next.

## Generating an experiment
To make your own experiment, you have to create an experiment folder like the one in this subdirectory, or like the [synthea experiments folder](../experiments/synthea-breast-cancer/winter2022/Federated/experiment). Place this experiment folder inside your own experiment subdirectory within the larger `experiments` root subdirectory (eg. `experiments/my-new-experiment/experiment/`). Ensure that you have at least the 8 files present in the example folder, within your new folder. Don't change the names or parameters of the items that will be imported through the \_\_init\_\_.py file (eg. `experiment`, `model`, `FlowerClient` & `eval_fn`, etc.), but feel free to change the names of other items (eg. `MockExperiment`) - Just ensure you have made the changes to the name in all places required. If you have any extra files you want to add to the experiment, create a subdirectory within the `experiment` folder called `helpers`, that houses any such functions. An example of this can be found within the [synthea experiments folder](../experiments/synthea-breast-cancer/winter2022/Federated/experiment).

## Running an experiment

In order to run the experiment, it makes the most sense to create your own `quickstart.sh` script to get the required docker services up in order with the parameters you need. For example, for the Winter 2022 Synthea dataset, use the following line of code from the root of the federated learning directory:

```bash
./experiments/synthea-breast-cancer/winter2022/Federated/quickstart.sh -i <INGEST-PATH> -p <PORT> -n <NUM-OF-SITES> -r <NUM-OF-ROUNDS> -e <PATH-TO-EXPERIMENT-DIRECTORY>
```