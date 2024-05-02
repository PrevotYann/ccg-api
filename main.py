from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routers import cardsets, ebay, users

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
    openapi_url="/api/openapi.json"
)

app.include_router(cardsets.router)
app.include_router(ebay.router)
app.include_router(users.router)

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
