# models.py
"""
This module is dedicated for all the pydantic models the API will use.
"""
from pydantic import BaseModel


class Candidate(BaseModel):
    """
    This class is a pydantic model for the candidate.
    """
    name: str
    email: str
    phone: str
    cv: str
