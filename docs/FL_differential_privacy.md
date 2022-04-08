# Differentially Private Federated Learning Experiment

There are a few aspects to consider when implementing a differentially private algorithm: 
-  Find a balance between epsilon and the accuracy

- Add noise at the fl-client-training level, for datapoint-level privacy. It will be desirable to also add noise at the fl-server level (for federation-member-level privacy) but that is out-of-scope for this specific experiment.

- Algorithm than can coexist with the current federated-learning architecture


## Algorithm Implemented
A `diffprivlib` implementation would apply differential privacy at the fl-client level. This would have the effect of minimzing the impact that any particular data point would have on the analysis of the dataset as a whole. 

The [confluence document](https://candig.atlassian.net/wiki/spaces/CA/pages/634224664/Synthea+Breast+Cancer+-+Choice+of+Differential+Privacy+Algorithm) associated with this story delves deeper into the decision.

## Implementing a Custom Differential Privacy Algorithm
To implement your own differential privacy algorithm, you may need to either:
- Change the model you are using to one that incorporates differential privacy.
- Modify the strategy implemented. Perhaps you want to implement a strategy that is not Federated Averaging. In that case, build your own child class of the [`Strategy`](https://github.com/adap/flower/blob/main/src/py/flwr/server/strategy/strategy.py) Abstract Base Class. That said, you will need to include parameters for `on_fit_config_fn`, `eval_fn` and `min_available_clients`, similar in nature to the [FedAvg](https://github.com/adap/flower/blob/main/src/py/flwr/server/strategy/fedavg.py) implementation to ensure compatibility with the fl-server.

You can consolidate these changes within a new `experiment` folder and mount that to the fl-server and fl-clients to get a differential-privacy-enabled experiment running. 

Although it is not recommended, if your code for the differential-privacy experiment is similar to the non-differentially-private experiment, you may want to implement a quickstart script similar to the one present in `experiments/synthea-breast-cancer/winter2022/Differentially-Private/quickstart.sh` which simply borrows the code from `experiments/synthea-breast-cancer/winter2022/Federated/experiment`, and replaces the files it doesn't need with their replacements from its own `experiment` folder. If you follow this method, don't make use of docker volumes or you will overwrite the non-differentially-private code with its differentially-private counterpart.

## Future Improvements / Technical Debt
- Improve [our implementation](https://github.com/CanDIG/federated-learning/blob/main/services/fl-server/server.py) of the [fl-server](https://github.com/adap/flower/blob/main/src/py/flwr/server/app.py#L32) to be able to take a [`Server`](https://github.com/adap/flower/blob/main/src/py/flwr/server/server.py#L53) object. This would allow people to change the Server backend to whatever they wish, if they so choose.
- Improve our implementation of the `fl-server` to be able to take an instance of a Strategy object that doesn't have the parameters `on_fit_config_fn`, `eval_fn` and `min_available_clients`. This would allow the Strategy to be much more flexible.