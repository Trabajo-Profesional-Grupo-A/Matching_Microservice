"""
This module contains the API endpoints for the matching service.
"""

import os
from typing import List
from resume_parsing.scripts import JobDescriptionProcessor
from resume_parsing.scripts.ResumeProcessor import ResumeProcessor
import requests
from fastapi import (
    APIRouter,
    HTTPException,
)
import firebase_admin
from firebase_admin import credentials, storage

API_USERS_URL="https://users-microservice-mmuh.onrender.com"
API_COMPANIES_URL="https://companies-microservice.onrender.com"

cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(cred, {"storageBucket": "tpp-grupoa.appspot.com"})
bucket = storage.bucket()

from config.setup import model, index_cv, index_jd

from control.codes import (
    BAD_REQUEST,
)
from control.models.models import DataJD, JobDescription, ModelData, ResumeFields

router = APIRouter(
    tags=["Matching"],
)
origins = ["*"]


@router.post("/matching/candidate/{user_email}/")
def upload_candidate(user_email: str, user_model_data: ModelData):
    try:
        candidate_vector = model.infer_vector(user_model_data.model_data.split())
        
        index_cv.upsert(
            vectors=[
                {"id": user_email, "values": candidate_vector},
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
                {"id": job_id, "values": job_vector},
            ],
            namespace="ns1"
        )
    except Exception as error:
        raise HTTPException(status_code=BAD_REQUEST, detail=str(error)) from error
    return {"message": "Job uploaded successfully"}

@router.get("/matching/candidate/{job_id}/", response_model=List[str])
def get_candidates(job_id: str, k: int = 10):
    try:
        job_vector = index_jd.fetch(ids=[job_id], namespace="ns1")["vectors"].get(job_id)["values"]
        print("Vector del trabajo:", job_vector)

        n = round(2 * k, 0)

        print(int(n))
        candidates = index_cv.query(vector=job_vector, include_values = True, top_k=int(n), namespace="ns1")

        ids = {}
        for candidate in candidates.get("matches"):
            ids[candidate["id"]] = candidate["score"]

        url = API_COMPANIES_URL + f"/companies/company/job_description_to_match/{job_id}/"
        jd_data = requests.get(
            url
        )
        print(jd_data)
        jd_data = jd_data.json()

        score_list = {}

        print("candidates", ids)

        dict_jd = JobDescriptionProcessor(' '.join([jd_data["title"], jd_data["description"], ' '.join(jd_data["responsabilities"]), ' '.join(jd_data["requirements"])])).process()

        jd_data["pos_frequencies"] = dict_jd["pos_frequencies"]
        jd_data["keyterms"] = dict_jd["keyterms"]
        jd_data["keywords_tfidf"] = dict_jd["keywords_tfidf"]


        for email, score in ids.items():
            url = API_USERS_URL + f"/users/user/resume/{email}/"
            resume_fields = requests.get(
                url
            )
            
            resume_fields = resume_fields.json()

            print("User", resume_fields)
            print("JD", jd_data)
            print("Score", score)

            print("1")

            # Job title match weight
            job_title_weight = 1.5 if jd_data['title'] in resume_fields["job_titles"] else 1.0
            print("2")

            # Requirements match weight
            requirements_weight = 1.0
            for req in jd_data['requirements']:
                if req not in resume_fields["skills"] and req not in resume_fields["model_data"]:
                    requirements_weight -= 0.1
                    if requirements_weight < 0:
                        requirements_weight = 0
                        return 0
                    
            print("3")

            print("pos_frequencies", jd_data['pos_frequencies'])
            # Pos frequencies weight
            pos_freq_weight = 1.0
            for word in jd_data['pos_frequencies'].keys():
                if word in resume_fields["model_data"]:
                    pos_freq_weight += 0.1

            # Keyterms and keywords_tfidf weight
            keyterms_weight = 1.0
            print("key terms", jd_data['keyterms'])
            for term in jd_data['keyterms']:
                if term[0] in resume_fields["model_data"]:
                    keyterms_weight += 0.1
            
            print("keywords_tfidf", jd_data['keywords_tfidf'])
            for keyword in jd_data['keywords_tfidf']:
                if keyword in resume_fields["model_data"]:
                    keyterms_weight += 0.1

            # Calculate final weighted similarity score
            final_similarity_score = score * job_title_weight * requirements_weight * pos_freq_weight * keyterms_weight
            score_list[email] = final_similarity_score

            print("4")
        
        top_k_mayores = dict(sorted(score_list.items(), key=lambda item: item[1], reverse=True)[:k])
        
        print("Candidatos:", list(top_k_mayores.keys()))
        print("top_k_mayores", top_k_mayores)
        return list(top_k_mayores.keys())
    except Exception as error:
        raise HTTPException(status_code=BAD_REQUEST, detail=str(error)) from error

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

        blob = bucket.blob(file_name)

        if not blob.exists(): 
            raise HTTPException(status_code=404, detail="File not found")
        
        blob.download_to_filename(file_path)

        resume_dict = ResumeProcessor(file_path).process()

        print("education", resume_dict["education"])
        
        return ResumeFields(
            education=resume_dict["education"],
            experience=resume_dict["experience"],
            job_titles=resume_dict["job_title"],
            skills=resume_dict["skills"],
            model_data=resume_dict["model_data"]
        )
    #http://YOUR_VM_IP:8000
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)