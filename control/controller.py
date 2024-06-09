from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from control.routers import matching
from annoy import AnnoyIndex
from scipy.spatial.distance import cosine

app = FastAPI(
    title="Matching API", description="This is the API for the matching service."
)

origins = ["*"]
app.include_router(matching.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
