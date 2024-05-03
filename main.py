import uvicorn

from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session


from app.routers import cardsets, ebay, users
from app.database import get_db
from app.models import Cardset

tagsMetadata = [
    {
        "name": "ebay",
        "description": "ebay relative routes",
    },
    {
        "name": "cardsets",
        "description": "cardset routes",
    },
]

app = FastAPI(
    title="CCG API",
    description="API for CCG APP",
    version="0.0.1",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    tagsMetadata=tagsMetadata
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cardsets.router)
app.include_router(ebay.router)
app.include_router(users.router)

@app.get("/")
async def docs_redirect():
    response = RedirectResponse(url="/api/docs")
    return response

@app.get("/hello")
def hello():
    return("Hello World!")

@app.get("/cardsets/main",
            tags=["cardsets"]
)
def get_all_cardsets(db: Session = Depends(get_db)):
    return db.query(Cardset).all()


if __name__ == "__main__":
    uvicorn.run("module_name:app", host="127.0.0.1", port=8000, reload=True)