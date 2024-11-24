import uvicorn

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routers import cardmarket, cardsets, ebay, fftcg_cards, items, narutokayou_cards, pokemon_cards, users, yugioh_cards

tagsMetadata = [
    {
        "name": "cards",
        "description": "cards routes for all CCGs",
    },
    {
        "name": "cardsets",
        "description": "cardset routes",
    },
    {
        "name": "ebay",
        "description": "ebay relative routes",
    },
    {
        "name": "cardmarket",
        "description": "cardmarket routes for all CCGs",
    },
    {
        "name": "items",
        "description": "items relative routes",
    }
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

app.include_router(pokemon_cards.router)
app.include_router(yugioh_cards.router)
app.include_router(fftcg_cards.router)
app.include_router(narutokayou_cards.router)
app.include_router(cardsets.router)
app.include_router(ebay.router)
app.include_router(cardmarket.router)
app.include_router(items.router)
app.include_router(users.router)

@app.get("/")
async def docs_redirect():
    response = RedirectResponse(url="/api/docs")
    return response

@app.get("/hello")
def hello():
    return("Hello World!")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)