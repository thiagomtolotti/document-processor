from fastapi.routing import APIRouter

router = APIRouter()


@router.get("/")
def ping():
    return {"message": "Service is alive"}
