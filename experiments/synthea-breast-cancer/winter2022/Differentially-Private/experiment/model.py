import diffprivlib.models as dp
import experiment.settings

model = dp.LogisticRegression(
    max_iter=experiment.settings.FL_EPOCHS,
    warm_start=True
)