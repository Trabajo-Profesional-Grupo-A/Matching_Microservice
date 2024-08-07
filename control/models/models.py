# models.py
"""
This module is dedicated for all the pydantic models the API will use.
"""
from typing import List, Tuple
from pydantic import BaseModel


class Candidate(BaseModel):
    """
    This class is a pydantic model for the candidate.
    """
    name: str
    email: str
    phone: str
    cv: str

class ResumeFields(BaseModel):
    """
    Resume fields model.
    """
    education: str
    experience: str
    job_titles: List[str]
    skills: List[str]
    model_data: str

class DataJD(BaseModel):
    """
    Data JD model.
    """
    id: int
    model_data: str

class JobDescription(BaseModel):
    """
    Job description model.
    """
    title: str
    description: str
    responsabilities: List[str]
    requirements: List[str]
    work_model: str
    age_range: Tuple[int, int]

class ModelData(BaseModel):
    """
    Model data model.
    """
    model_data: str
