# Differentially Private Federated Learning Experiment

There are a few aspects to consider when implementing a differentially private algorithm: 
-  Find a balance between epsilon and the accuracy

- Add noise at the fl-client-training level, for datapoint-level privacy. It will be desirable to also add noise at the fl-server level (for federation-member-level privacy) but that is out-of-scope for this specific experiment.

- Algorithm than can coexist with the current federated-learning architecture


## Algorithm Implemented
A `diffprivlib` implementation would apply differential privacy at the fl-client level. This would have the effect of minimzing the impact that any particular data point would have on the analysis of the dataset as a whole. 

The [confluence document](https://candig.atlassian.net/wiki/spaces/CA/pages/634224664/Synthea+Breast+Cancer+-+Choice+of+Differential+Privacy+Algorithm) associated with this story delves deeper into the decision.