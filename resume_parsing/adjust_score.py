# from collections import defaultdict

# import numpy as np
# from numpy.linalg import norm


# def match_key_requirements(jd_skills, cv_skills):
#     missing_skills = [skill for skill in jd_skills if skill not in cv_skills]
#     return missing_skills

# def assign_weights(skills_list):
#     weights = defaultdict(int)
#     for skill in skills_list:
#         weights[skill] = 2  # Assign a higher weight to key skills
#     return weights


# def weighted_cosine_similarity(vec1, vec2, weights):
#     weighted_vec1 = np.array([weights.get(word, 1) for word in vec1])
#     weighted_vec2 = np.array([weights.get(word, 1) for word in vec2])

#     # Apply the weights to the original vectors
#     weighted_v1 = vec1 * weighted_vec1
#     weighted_v2 = vec2 * weighted_vec2

#     similarity = 100 * np.dot(weighted_v1, weighted_v2) / (norm(weighted_v1) * norm(weighted_v2))
#     return similarity

# def rule_based_filter(cv_text, jd_requirements):
#     for requirement in jd_requirements:
#         if requirement not in cv_text:
#             return False
#     return True

# def match_cv_jd(cv_text, jd_text, jd_requirements):

#     cv_text_processed = preprocess_text_CV_JD(cv_text)
#     jd_text_processed = preprocess_text_CV_JD(jd_text)

#     if not rule_based_filter(cv_text_processed, jd_requirements):
#         return 0  # Discard CV if it does not meet the requirements

#     cv_vector = model.infer_vector(cv_text_processed.split())
#     jd_vector = model.infer_vector(jd_text_processed.split())

#     jd_skills = extract_skills_experience(jd_text)
#     cv_skills = extract_skills_experience(cv_text)

#     missing_skills = match_key_requirements(jd_skills, cv_skills)
#     if missing_skills:
#         return 0  # Discard CV if key skills are missing

#     weights = assign_weights(jd_skills)
#     similarity = weighted_cosine_similarity(cv_vector, jd_vector, weights)

#     return similarity

# job_description = """
# We are looking for a Senior Python Developer with 5 years of experience in Python.
# Must have experience with Django and Flask, as well as front-end technologies like React.
# Experience with Docker and Kubernetes is a plus.
# """

# cv = """
# I am an experienced developer with over 6 years in Python.
# I have worked extensively with just Flask.
# Additionally, I have experience with React and have used Docker in several projects.
# """
# # Extract key requirements from the job description manually or using a parser
# jd_requirements = ["python", "5 years of experience in Python", "django", "flask", "react"]

# # Model evaluation
# model = Doc2Vec.load('/content/cv_job_maching_vector_size_10_min_count_5_window_5_epochs_50.model')
# # Calculate the similarity score
# similarity_score = match_cv_jd(cv, job_description, jd_requirements)

# print(f"Similarity Score: {similarity_score}")




# resume_fields.model_data = "This is a sample text for the model data field."
# data_jd.model_data = "This is a sample text for the model data field."

# # Load pre-trained Doc2Vec model (ensure the model is trained or downloaded)
# doc2vec_model = Doc2Vec.load('path/to/doc2vec_model')

# # Infer vectors using Doc2Vec
# resume_vector = doc2vec_model.infer_vector(resume_fields.model_data.split())
# jd_vector = doc2vec_model.infer_vector(data_jd.model_data.split())

# # Pinecone
# cosine_similarity = 1

# # Adjust weights based on specific criteria

# # Job title match weight
# job_title_weight = 1.5 if jd_data['job_title'] in resume_fields.job_titles else 1.0

# # Requirements match weight
# requirements_weight = 1.0
# for req in jd_data['requirements']:
#     if req not in resume_fields.skills and req not in resume_fields.model_data:
#         requirements_weight -= 0.1
#         if requirements_weight < 0:
#             requirements_weight = 0
#             return 0

# # Pos frequencies weight
# pos_freq_weight = 1.0
# for word in data_jd['pos_frequencies'].keys():
#     if word in resume_clean_data:
#         pos_freq_weight += 0.1

# # Keyterms and keywords_tfidf weight
# keyterms_weight = 1.0
# for term in data_jd['keyterms']:
#     if term[0] in resume_clean_data:
#         keyterms_weight += 0.1
# for keyword in data_jd['keywords_tfidf']:
#     if keyword in resume_clean_data:
#         keyterms_weight += 0.1

# # Calculate final weighted similarity score
# final_similarity_score = cosine_similarity * job_title_weight * requirements_weight * pos_freq_weight * keyterms_weight

# print(f"Final Similarity Score: {final_similarity_score}")
