"""
This module contains the API endpoints for the matching service.
"""

from fastapi import (
    APIRouter,
    HTTPException,
)

from config.setup import model, index

from control.codes import (
    BAD_REQUEST,
)

router = APIRouter(
    tags=["Matching"],
)
origins = ["*"]


@router.post("/matching/candidate/{user_id}/")
def upload_candidate(user_id: int, candidate: str):
    """

    """
    try:
        # 2. llamar a la capa de service para que:
            # 2.1. preprocese el cv (limpieza de datos, tokenizacion, etc)
            vector = model.infer_vector(candidate.split())
            print(vector)
            index.upsert([vector])

            # 2.2. llame a la capa de matching para que compare el cv con las ofertas
            # 2.3. avise a las empresas con las que hizo matching
    except Exception as error:
        raise HTTPException(status_code=BAD_REQUEST, detail=str(error)) from error
    return {"message": "Candidate uploaded successfully"}

@router.post("/matching/job")
def upload_job(job_id: int, job: str):
    """

    """
    try:
        pass
    except Exception as error:
        raise HTTPException(status_code=BAD_REQUEST, detail=str(error)) from error
    return {"message": "Job uploaded successfully"}

@router.get("/matching/candidate/{job_id}/")
def get_candidates(job_id: int, k: int = 10):
    """

    """
    try:
        pass
    except Exception as error:
        raise HTTPException(status_code=BAD_REQUEST, detail=str(error)) from error
    return {"message": "Candidates retrieved successfully"}
    #return generate_response_candidates()


# # Ruta para buscar vecinos más cercanos
# @app.get("/search_nearest_neighbors/")
# async def search_nearest_neighbors(query_vector: List[float]):
#     """
#     Endpoint to search for nearest neighbors given a query vector.
#     """
#     nearest_neighbors = annoy_index.get_nns_by_vector(query_vector, 10, include_distances=True)  # Buscar los 10 vecinos más cercanos
#     # Calcular la distancia del coseno para cada vecino
#     nearest_neighbors_with_distances = [(neighbor, cosine(query_vector, annoy_index.get_item_vector(neighbor))) for neighbor in nearest_neighbors]
#     return {"nearest_neighbors": nearest_neighbors_with_distances}

