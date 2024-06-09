import pinecone
import pickle

API_KEY = "c70f6e97-c3ad-402e-9210-0325a3381fde"
ENVIROMENT = "us-east-1"
INDEX_NAME = "job-cv-matching"
MODEL_PATH = "./models/cv_job_maching_vector_size_10_min_count_5_window_3_epochs_50.model"



model = pickle.load(open(MODEL_PATH, "rb"))
# Conect with pinecone, api_key brandon = "26250ae5-a575-4c67-bdd0-517f8f788c48"
pinecone.init(api_key=API_KEY, environment=ENVIROMENT)
index = pinecone.Index(INDEX_NAME)