"""
This module contains the API endpoints for the matching service.
"""

import os
from resume_parsing.scripts import JobDescriptionProcessor
from resume_parsing.scripts.ResumeProcessor import ResumeProcessor

from fastapi import (
    APIRouter,
    HTTPException,
)
import firebase_admin
from firebase_admin import credentials, storage

cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(cred, {"storageBucket": "tpp-grupoa.appspot.com"})
bucket = storage.bucket()

from config.setup import model, index_cv, index_jd

from control.codes import (
    BAD_REQUEST,
)
from control.models.models import DataJD, JobDescription, ResumeFields

router = APIRouter(
    tags=["Matching"],
)
origins = ["*"]


@router.post("/matching/candidate/{user_email}")
def upload_candidate(user_email: str, user_model_data: str):
    try:
        candidate_vector = model.infer_vector(user_model_data.split())
        
        index_cv.upsert(
            vectors=[
                {"email": user_email, "values": candidate_vector},
            ],
            namespace="ns1"
        )
    
    except Exception as error:
        raise HTTPException(status_code=BAD_REQUEST, detail=str(error)) from error
    return {"message": "Candidate uploaded successfully"}

@router.post("/matching/job/{job_id}/")
def upload_job(job_id: str, job_description: JobDescription):
    try:
        print("Me llego una job desc")
        print("job_id", job_id)
        print("job_description", job_description)

        model_data = ""
        model_data += job_description.title + " "
        model_data += job_description.description + " "
        model_data += " ".join(job_description.responsabilities) + " "
        model_data += " ".join(job_description.requirements) + " "

        dict = JobDescriptionProcessor(model_data).process()

        job_vector = model.infer_vector(dict["model_data"].split())

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
def get_candidates(job_id: str, k: int = 10):
    try:
        job_vector = index_jd.fetch(ids=[job_id], namespace="ns1")["vectors"].get(job_id)["values"]
        print("Vector del trabajo:", job_vector)
        
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
def delete_job(job_id: str):
    try:
        index_jd.delete(ids=[job_id], namespace="ns1")
    except Exception as error:
        raise HTTPException(status_code=BAD_REQUEST, detail=str(error)) from error
    return {"message": "Job deleted successfully"}

@router.get("/user/fields", response_model=ResumeFields)
def get_fields_of_cv(email: str):
    file_name = f"resumes/{email}.pdf"
    file_path = f"/tmp/{email}.pdf"

    try:
        print("antes del blob")
        print(" file_name", file_name)
        blob = bucket.blob(file_name)
        print("blob", blob)
        print("despues del blob")
        if not blob.exists(): 
            raise HTTPException(status_code=404, detail="File not found")
        print("antes del download to filename")
        blob.download_to_filename(file_path)
        print("despues del download to filename")
        
        print("File path", file_path)

        dict = ResumeProcessor(file_path).process()

        return ResumeFields(
            education=dict["education"],
            experience=dict["experience"],
            job_titles=dict["job_title"],
            skills=dict["skills"],
            model_data=dict["model_data"]
        )
    #http://YOUR_VM_IP:8000
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# @router.get("/company/data", response_model=DataJD)
# def get_data_of_jd_str(jd: str):
#     try:
#         dict = JobDescriptionProcessor(jd).process()

#         return DataJD(
#             id=dict["id"],
#             model_data=dict["model_data"]
#         )
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# {
#   "title": "front end developer",
#   "description": "react js typescript",
#   "responsabilities": [
#     "work", "to be in time"
#   ],
#   "requirements": [
#     "html", "css"
#   ]
# }

#token messi eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6Im1lc3NpIn0.tvDJgzGCRv_FAD4gT006nfElL1TjVoRZkhDmBC8Ma10