from sklearn.linear_model import LogisticRegression
import experiment.settings

model = LogisticRegression(
    solver=experiment.settings.FL_SOLVER,
    random_state=experiment.settings.FL_RANDOM_STATE,
    max_iter=experiment.settings.FL_EPOCHS,
    warm_start=True
)