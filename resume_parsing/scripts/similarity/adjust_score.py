from collections import defaultdict

import numpy as np
from numpy.linalg import norm


def match_key_requirements(jd_skills, cv_skills):
    missing_skills = [skill for skill in jd_skills if skill not in cv_skills]
    return missing_skills

def assign_weights(skills_list):
    weights = defaultdict(int)
    for skill in skills_list:
        weights[skill] = 2  # Assign a higher weight to key skills
    return weights


def weighted_cosine_similarity(vec1, vec2, weights):
    weighted_vec1 = np.array([weights.get(word, 1) for word in vec1])
    weighted_vec2 = np.array([weights.get(word, 1) for word in vec2])

    # Apply the weights to the original vectors
    weighted_v1 = vec1 * weighted_vec1
    weighted_v2 = vec2 * weighted_vec2

    similarity = 100 * np.dot(weighted_v1, weighted_v2) / (norm(weighted_v1) * norm(weighted_v2))
    return similarity

def rule_based_filter(cv_text, jd_requirements):
    for requirement in jd_requirements:
        if requirement not in cv_text:
            return False
    return True

def match_cv_jd(cv_text, jd_text, jd_requirements):

    cv_text_processed = preprocess_text_CV_JD(cv_text)
    jd_text_processed = preprocess_text_CV_JD(jd_text)

    if not rule_based_filter(cv_text_processed, jd_requirements):
        return 0  # Discard CV if it does not meet the requirements

    cv_vector = model.infer_vector(cv_text_processed.split())
    jd_vector = model.infer_vector(jd_text_processed.split())

    jd_skills = extract_skills_experience(jd_text)
    cv_skills = extract_skills_experience(cv_text)

    missing_skills = match_key_requirements(jd_skills, cv_skills)
    if missing_skills:
        return 0  # Discard CV if key skills are missing

    weights = assign_weights(jd_skills)
    similarity = weighted_cosine_similarity(cv_vector, jd_vector, weights)

    return similarity
