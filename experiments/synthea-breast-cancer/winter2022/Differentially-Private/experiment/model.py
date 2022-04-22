import diffprivlib.models as dp
import experiment.settings

model = dp.LogisticRegression(
    max_iter=experiment.settings.FL_EPOCHS,
    epsilon=experiment.settings.FL_EPSILON,
    warm_start=True
)
