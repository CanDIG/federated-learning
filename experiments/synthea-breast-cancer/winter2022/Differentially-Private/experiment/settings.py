import os

FL_N_CLASSES = 4
FL_N_FEATURES = 7
FL_EPOCHS = 10000
FL_EPSILON = 0.85
FL_MIN_CLIENTS = 2
FL_RANDOM_STATE = 1729
FL_TABLE_FILE = f"{os.getcwd()}/experiment/helpers/tables.txt"
FL_CHECKPOINT_PATH = 'experiment/checkpoints'

FL_ROUNDS = int(os.getenv("ROUNDS", "100"))
FL_CLIENT_NUMBER = os.getenv("FLOWER_CLIENT_NUMBER", "1")
FL_INTERNAL_PORT = os.getenv("SERVER_INTERNAL_PORT", "8080")
FL_INTERNAL_HOST = os.getenv("SERVER_INTERNAL_HOST", "0.0.0.0")
FL_SERVER_URL = os.getenv('FLOWER_SERVER_URL', "http://127.0.0.1:5000")
FL_GRAPHQL_URL = os.getenv("GRAPHQL_INTERFACE_URL", "http://127.0.0.1:5000")
