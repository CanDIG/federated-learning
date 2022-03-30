from sklearn.linear_model import LogisticRegression

model = LogisticRegression(
    solver='saga',
    random_state=1729,
    max_iter=10000,
    warm_start=True
)