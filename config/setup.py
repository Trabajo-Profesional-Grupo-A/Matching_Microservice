from pinecone import Pinecone, ServerlessSpec
from gensim.models import Doc2Vec


API_KEY = "6a195f34-4ee8-40cd-9036-909e2b651a9c"
INDEX_CV = "cv-vectors"
INDEX_JD = "jd-vectors"
MODEL_PATH = "./models/cv_job_maching_vector_size_10_min_count_5_window_3_epochs_50.model"


# Cargar el modelo
model = Doc2Vec.load(MODEL_PATH)
# Conect with pinecone, api_key brandon = "26250ae5-a575-4c67-bdd0-517f8f788c48"

pc = Pinecone(api_key=API_KEY)

if INDEX_CV not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_CV, 
        dimension=model.vector_size, 
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
          )
      )
    
if INDEX_JD not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_JD, 
        dimension=model.vector_size, 
        metric='cosine',
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
          )
      )


# Connect to the index
index_cv = pc.Index(INDEX_CV)
index_jd = pc.Index(INDEX_JD)
