from fastapi import APIRouter, FastAPI

app = FastAPI()

router = APIRouter()


@router.get("/")
def ping():
    return {"message": "Service is alive"}


app.include_router(router)
