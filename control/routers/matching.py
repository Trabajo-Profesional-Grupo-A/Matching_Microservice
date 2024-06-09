"""
This module contains the API endpoints for the matching service.
"""

from fastapi import (
    APIRouter,
    HTTPException,
)

from config.setup import model, index_cv, index_jd

from control.codes import (
    BAD_REQUEST,
)

router = APIRouter(
    tags=["Matching"],
)
origins = ["*"]


@router.post("/matching/candidate/{user_id}/")
def upload_candidate(user_id: int, candidate_text: str):
    try:
        #Preprocesar el texto

        candidate_vector = model.infer_vector(candidate_text.split())

        print("Vector del candidato:", candidate_vector)
        
        index_cv.upsert(
            vectors=[
                {"id": str(user_id), "values": candidate_vector},
            ],
            namespace="ns1"
        )
    
    except Exception as error:
        raise HTTPException(status_code=BAD_REQUEST, detail=str(error)) from error
    return {"message": "Candidate uploaded successfully"}

@router.post("/matching/job/{job_id}/")
def upload_job(job_id: int, job: str):
    try:
        #Preprocesar el texto

        job_vector = model.infer_vector(job.split())

        print("Vector del candidato:", job_vector)
        
        index_jd.upsert(
            vectors=[
                {"id": str(job_id), "values": job_vector},
            ],
            namespace="ns1"
        )
    except Exception as error:
        raise HTTPException(status_code=BAD_REQUEST, detail=str(error)) from error
    return {"message": "Job uploaded successfully"}

@router.get("/matching/candidate/{job_id}/")
def get_candidates(job_id: int, k: int = 10):
    try:
        job_vector = index_jd.fetch(ids=[str(job_id)], namespace="ns1")["vectors"].get(str(job_id))["values"]
        print("Vector del trabajo:", job_vector)
        print(k)
        candidates = index_cv.query(vector=job_vector, include_values = True, top_k=k, namespace="ns1")
        print("Candidatos:", candidates)
    except Exception as error:
        raise HTTPException(status_code=BAD_REQUEST, detail=str(error)) from error
    return candidates["matches"][0].get("id")

@router.delete("/matching/candidate/{user_id}/")
def delete_candidate(user_id: int):
    try:
        index_cv.delete(ids=[str(user_id)], namespace="ns1")
    except Exception as error:
        raise HTTPException(status_code=BAD_REQUEST, detail=str(error)) from error
    return {"message": "Candidate deleted successfully"}

@router.delete("/matching/job/{job_id}/")
def delete_job(job_id: int):
    try:
        index_jd.delete(ids=[str(job_id)], namespace="ns1")
    except Exception as error:
        raise HTTPException(status_code=BAD_REQUEST, detail=str(error)) from error
    return {"message": "Job deleted successfully"}

