from fastapi import APIRouter


router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/", status_code=200)
def get_health():
    return {"status": "healthy"}
