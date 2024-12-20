"""
This module contains the API endpoints for the matching service.
"""

import os
from typing import List
from resume_parsing.location import get_coordinates_locationiq
from resume_parsing.retrain import retrain
from resume_parsing.scripts import JobDescriptionProcessor
from resume_parsing.scripts.TextCleaner import TextCleaner
from resume_parsing.scripts.Extractor import DataExtractor
from resume_parsing.scripts.ResumeProcessor import ResumeProcessor
from geopy.distance import geodesic
from concurrent.futures import ThreadPoolExecutor
import threading

executor = ThreadPoolExecutor(max_workers=1)
#executor2 = ThreadPoolExecutor(max_workers=1)

import requests
from fastapi import (
    APIRouter,
    HTTPException,
)
from gensim.models import Doc2Vec

import firebase_admin
from firebase_admin import credentials, storage

API_USERS_URL="https://users-microservice-mmuh.onrender.com"
API_COMPANIES_URL="https://companies-microservice.onrender.com"
API_NOTIFICATION_URL="https://notification-microservice-xc3v.onrender.com"

API_LOCATION_KEY = "pk.16ff76ca0f92be97f397a3683dae4e14"
AMOUNT_COMPANIES_CHECK = 3


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

def retrain_in_background():
    global model
    print("Arraco a entrenar")
    retrain()  # Reentrena el modelo
    print("Termine de entrenar")


    model = Doc2Vec.load('./models/cv_job_maching_vector_size_10_min_count_5_window_3_epochs_50.model')  # Carga el nuevo modelo

def check_new_match(user_email):
    print("coso de brandon", index_jd.list(namespace='ns1'))
    
    job_ids = []
    for ids in index_jd.list(namespace='ns1'):
        job_ids.append(ids)


    print("job_ids", job_ids[0])
        
    for job_id in job_ids[0]:
        top_candidates = get_top_candidates(job_id, AMOUNT_COMPANIES_CHECK)

        print(f"top_candidates para id {job_id}: {list(top_candidates.keys())}")

        if list(top_candidates.keys())[0] == user_email:
            print("Match encontrado")

            print("job_id", job_id)

            url = f"{API_COMPANIES_URL}/companies/company/job_description_to_notify/{job_id}"

            response = requests.get(url)

            jd_title = response.json()["title"]
            email_user = response.json()["email"]

            print("jd_title", jd_title)
            print("email_user", email_user)

            data = {
                "email_sender": "app",
                "email_receivers": [
                    email_user
                ],
                "title": f"New Candidate for {jd_title}",
                "body": "There's a new candidate who could be a perfect match. Check out his profile now.",
                "data": {"email_candidate": user_email},
                "type": "new_candidate",
                "name_sender": "app",
                "avatar_sender": "app"
            }

            print("data", data)

            url = f"{API_NOTIFICATION_URL}/notifications/device-token/send"

            print("url", url)
            try:
                requests.post(url, json=data)
            except Exception as e:
                print("Error en el request")
                print(e)

            print("Notificacion enviada")


@router.post("/matching/candidate/{user_email}/")
def upload_candidate(user_email: str, user_model_data: ModelData):
    try:
        global model
        candidate_vector = model.infer_vector(user_model_data.model_data.split())
        
        index_cv.upsert(
            vectors=[
                {"id": user_email, "values": candidate_vector},
            ],
            namespace="ns1"
        )

        executor.submit(check_new_match, user_email)

    except Exception as error:
        raise HTTPException(status_code=BAD_REQUEST, detail=str(error)) from error
    return {"message": "Candidate uploaded successfully"}

@router.post("/matching/job/{job_id}/")
def upload_job(job_id: str, job_description: JobDescription):
    try:
        print("Me llego una job desc")
        print("job_id", job_id)
        print("job_description", job_description)

        print("var")

        model_data = ""
        model_data += job_description.title + " "
        model_data += job_description.description + " "
        model_data += " ".join(job_description.responsabilities) + " "
        model_data += " ".join(job_description.requirements) + " "

        dict = JobDescriptionProcessor(model_data).process()

        with open("./resume_parsing/Data/newJobDesc.csv", "a") as file:
            file.write(dict["model_data"] + "\n")

        global model

        job_vector = model.infer_vector(dict["model_data"].split())

        # Chequeo si hay que reentrenar
        print("lineas del archivo", len(open("./resume_parsing/Data/newJobDesc.csv").readlines()))
        if (len(open("./resume_parsing/Data/newJobDesc.csv").readlines()) % 50) == 0:
            print("retrain")
            executor.submit(retrain_in_background)


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
        top_k_mayores = get_top_candidates(job_id, k)
        
        return list(top_k_mayores.keys())
    except Exception as error:
        raise HTTPException(status_code=BAD_REQUEST, detail=str(error)) from error

def get_top_candidates(job_id, k):
    job_vector = index_jd.fetch(ids=[job_id], namespace="ns1")["vectors"].get(job_id)["values"]


    candidates = index_cv.query(vector=job_vector, include_values = True, top_k=50, namespace="ns1")

    ids = {}
    for candidate in candidates.get("matches"):
        ids[candidate["id"]] = candidate["score"]

    url = API_COMPANIES_URL + f"/companies/company/job_description_to_match/{job_id}/"
    jd_data = requests.get(
            url
        )

    jd_data = jd_data.json()

    score_list = {}

    dict_jd = JobDescriptionProcessor(' '.join([jd_data["title"], jd_data["description"], ' '.join(jd_data["responsabilities"]), ' '.join(jd_data["requirements"])])).process()

        #print("job description: ", dict_jd)

    jd_data["pos_frequencies"] = dict_jd["pos_frequencies"]
    jd_data["keyterms"] = dict_jd["keyterms"]
    jd_data["keywords_tfidf"] = dict_jd["keywords_tfidf"]

    requirements_skills = DataExtractor(' '.join(jd_data['requirements'])).extract_skills()
        
    requirements_education = DataExtractor(' '.join(jd_data['requirements'])).extract_education_title()

    print("requirements_skills: ", requirements_skills)
    print("requirements_education: ", requirements_education)

    for email, score in ids.items():
        print("Candidato: ", email)
        print("Score inicial: ", score)

        url = API_USERS_URL + f"/users/user/resume/{email}/"
        resume_fields = requests.get(
                url
            )
            
        resume_fields = resume_fields.json()

            #print("resume_fields del candidato", resume_fields)
        print("job_titles jd: ", jd_data['title'])
        print("job titles resume: ", resume_fields["job_titles"])

            # Job title match weight
        job_title_weight = 1.2 if jd_data['title'].lower() in resume_fields["job_titles"] else 1.0

        print("job_title_weight: ", job_title_weight)

            # Requirements match weight
        requirements_skills_weight = 1.0
        print("skills: ", resume_fields["skills"])
        print("model_data: ", resume_fields["model_data"])

        for req in requirements_skills:
            if req not in resume_fields["skills"] and req not in resume_fields["model_data"]:
                requirements_skills_weight -= 0.1
                if requirements_skills_weight < 0:
                    requirements_skills_weight = 0
                    break
            elif req in resume_fields["skills"] or req in resume_fields["model_data"]:
                requirements_skills_weight += 0.1

        print("requirements_skills_weight: ", requirements_skills_weight)

        requirements_education_weight = 1.0

        cleaned_education = TextCleaner(resume_fields["education"]).clean_text()

        for req in requirements_education:
            if req not in cleaned_education and req not in resume_fields["model_data"]:
                requirements_education_weight -= 0.1
                if requirements_education_weight < 0:
                    requirements_education_weight = 0
                    break
            elif req in cleaned_education or req in resume_fields["model_data"]:
                requirements_education_weight += 0.1
            
        print("requirements_education_weight: ", requirements_education_weight)
                    

            # Pos frequencies weight
        pos_freq_weight = 1.0
        for word in jd_data['pos_frequencies'].keys():
            if word in resume_fields["model_data"]:
                pos_freq_weight += 0.1
            
        print("pos_freq_weight: ", pos_freq_weight)

            # Keyterms and keywords_tfidf weight
        keyterms_weight = 1.0
        for term in jd_data['keyterms']:
            if term[0] in resume_fields["model_data"]:
                keyterms_weight += 0.1
            
        for keyword in jd_data['keywords_tfidf']:
            if keyword in resume_fields["model_data"]:
                keyterms_weight += 0.1

        print("keyterms_weight: ", keyterms_weight)

            

        location_weight = 1.0

        if jd_data["work_model"] == "on-site":
            company_coordinates = get_coordinates_locationiq(jd_data["address"], API_LOCATION_KEY)
            user_coordinates = get_coordinates_locationiq(resume_fields["address"], API_LOCATION_KEY)
            distance_km = geodesic(user_coordinates, company_coordinates).kilometers
            if distance_km > 50:
                location_weight = 0.3
            elif distance_km < 10:
                location_weight = 1.2
        elif jd_data["work_model"] == "hybrid":
            company_coordinates = get_coordinates_locationiq(jd_data["address"], API_LOCATION_KEY)
            user_coordinates = get_coordinates_locationiq(resume_fields["address"], API_LOCATION_KEY)
            distance_km = geodesic(user_coordinates, company_coordinates).kilometers
            if distance_km > 50:
                location_weight = 0.6
            elif distance_km < 10:
                location_weight = 1.1

        print("location_weight: ", location_weight)


            #calculate age weight
        age_weight = 1.0
        if resume_fields["age"] < jd_data["age_range"][0]:
            age_weight -= ((jd_data["age_range"][0] - resume_fields["age"]) * 0.04)

        elif resume_fields["age"] > jd_data["age_range"][1]:    
            age_weight -= ((resume_fields["age"] - jd_data["age_range"][1]) * 0.04)
        else:
            age_weight = 1.2

        print("age_weight: ", age_weight)

        job_preference_weight = 1.3

        print("job_preferences: ", resume_fields["job_preferences"])
            
        if resume_fields["job_preferences"]:
            job_preference_weight = 1.3 if jd_data['title'].lower() in resume_fields["job_preferences"] else 0.5

        print("job_preference_weight: ", job_preference_weight)

        years_of_experience_weight = 1.0
        if resume_fields["years_of_experience"] < jd_data["years_of_experience"]:
            years_of_experience_weight -= ((jd_data["years_of_experience"] - resume_fields["years_of_experience"]) * 0.04)

            # Calculate final weighted similarity score
        final_similarity_score = score * job_title_weight * requirements_skills_weight * requirements_education_weight * pos_freq_weight * keyterms_weight * location_weight * age_weight * job_preference_weight * years_of_experience_weight
            
        print("final_similarity_score: ", final_similarity_score)
            
        score_list[email] = final_similarity_score


        
    top_k_mayores = dict(sorted(score_list.items(), key=lambda item: item[1], reverse=True)[:k])
    return top_k_mayores

@router.delete("/matching/candidate/{email}/")
def delete_candidate(email: str):
    try:
        index_cv.delete(ids=[email], namespace="ns1")
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