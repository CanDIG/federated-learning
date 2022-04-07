# Differentially Private Federated Learning Experiment

There are three aspects to consider when implementing a differentially private algorithm. 
- The algorithm must find a balance between epsilon and the accuracy

- The more times applying the algorithm on the data, the more privacy loss

- Should be ideal for differential privacy at a datapoint level

- Add noise at the fl-client-training level instead of the fl-server level 

- Algorithm can coexist with the current federated-learning architecture

## Algorithm Implemented
A diffprivlib implementation would apply differential privacy at the fl-client level. This would have the effect of minimzing the impact that any particular data point would have on the analysis of the dataset as a whole. 

The [confluence document](https://candig.atlassian.net/wiki/spaces/~606c79f3edc14f00768afea5/pages/634028033/Choice+of+Differential+Privacy+Algorithm) associated with this story delves deeper into the decsion.