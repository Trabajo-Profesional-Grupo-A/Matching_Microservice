from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from control.routers import matching
import pinecone
import pickle
from annoy import AnnoyIndex
from scipy.spatial.distance import cosine

app = FastAPI(
    title="Matching API", description="This is the API for the matching service."
)

origins = ["*"]
app.include_router(matching.router)

@app.on_event("startup")
async def startup_event():
    """
    This function is called when the server starts.
    """
    model = pickle.load(open("/home/usaurio/Matching_Microservice/models/cv_job_maching_vector_size_10_min_count_5_window_3_epochs_50.model", "rb"))
    # Conect with pinecone, api_key brandon = "26250ae5-a575-4c67-bdd0-517f8f788c48"
    pinecone.init(api_key="c70f6e97-c3ad-402e-9210-0325a3381fde", environment="us-east-1")

    # Create a new index
    index_name = "job-cv-matching"
    pinecone.create_index(index_name, dimension=10, metric='cosine')

    # Connect to the index
    index = pinecone.Index(index_name)

# @app.on_event("startup")
# async def startup_event():
#     """
#     This function is called when the server starts.
#     """
#     model = pickle.load(open("/home/usaurio/Matching_Microservice/models/cv_job_maching_vector_size_10_min_count_5_window_3_epochs_50.model", "rb"))
    
#     annoy_index = AnnoyIndex(model.vector_size, 'angular')
#     for i in range(len(model.wv.index_to_key)):
#         annoy_index.add_item(i, model.wv[model.wv.index_to_key[i]])
#     annoy_index.build(10)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
