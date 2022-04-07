import diffprivlib.models as dp
import experiment.settings

model = dp.LogisticRegression(
    max_iter=experiment.settings.FL_EPOCHS,
    epsilon=experiment.settings.FL_EPSILON,
    warm_start=True
)

"""
This file has the only major differences (apart from settings.py not having an FL_SOLVER variable in this diff-priv experiment, and the requirements.txt files having 
diffprivlib added as a requirement) between the differentially-private and regular federated experiment. This is because the FL repo and flower are both quite 
modular, and also because the diffprivlib library extends the functionality of sklearn, which the original model was created from, and thus, not much had to be 
changed. The rest of the files in this `experiment` folder are practically identical. They are only copied from the Federated/experiment folder since we are working
 with a new experiment here.

The changes present in this file simply change the base model for our experiment, from the sklearn.LogisticRegression model, to the diffprivlib.models.LogisticRegression model. 
Given the nature of the new model, some of the older parameters added to the sklearn model are no longer here, such as the random_state and solver parameters.
"""
