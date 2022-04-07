# Differentially Private Federated Learning Experiment

There are a few aspects to consider when implementing a differentially private algorithm: 
-  We would like to find a balance between epsilon and the accuracy

- We would like to add noise at the fl-client-training level instead of the fl-server level 

- We want an algorithm than can coexist with the current federated-learning architecture

## Algorithm Implemented
A `diffprivlib` implementation would apply differential privacy at the fl-client level. This would have the effect of minimzing the impact that any particular data point would have on the analysis of the dataset as a whole. 

The [confluence document](https://candig.atlassian.net/wiki/spaces/CA/pages/634224664/Synthea+Breast+Cancer+-+Choice+of+Differential+Privacy+Algorithm) associated with this story delves deeper into the decision.