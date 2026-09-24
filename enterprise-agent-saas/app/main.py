from fastapi import FastAPI

from app.api.router import router
from app.services.database import Base, engine

app = FastAPI(title="Enterprise Agent SaaS", version="0.1.0")


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


app.include_router(router)
