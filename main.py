from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routers import ebay

tagsMetadata = [
    {
        "name": "ebay",
        "description": "ebay relative routes",
    },
]

app = FastAPI(openapi_tags=tagsMetadata)

app.include_router(ebay.router)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def docs_redirect():
    response = RedirectResponse(url="/docs")
    return response
