import uvicorn

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routers import cardsets, ebay, pokemon_cards, users, yugioh_cards

tagsMetadata = [
    {
        "name": "ebay",
        "description": "ebay relative routes",
    },
    {
        "name": "cardsets",
        "description": "cardset routes",
    },
    {
        "name": "cards",
        "description": "cards routes for all CCGs",
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
app.include_router(yugioh_cards.router)

@app.get("/")
async def docs_redirect():
    response = RedirectResponse(url="/api/docs")
    return response

@app.get("/hello")
def hello():
    return("Hello World!")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)