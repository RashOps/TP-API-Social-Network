from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.models.event import Event
from src.models.groupe import Groupe
from src.models.discussion import Discussion
from src.models.album import Album
from src.models.billetterie import Billetterie
from src.models.covoiturage import Covoiturage
from src.models.sondage import Sondage
from src.models.shopping_list import ShoppingItem
from src.models.user import User
from src.routes import (
    albums,
    billetteries,
    covoiturages,
    discussions,
    events,
    groupes,
    shopping_list,
    sondages,
    users,
)
from src.config import settings
from src.utils.db_client import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = await init_db(
        [
            User,
            Groupe,
            Event,
            Discussion,
            Album,
            Sondage,
            Billetterie,
            ShoppingItem,
            Covoiturage,
        ]
    )
    try:
        yield
    finally:
        await client.close()


app = FastAPI(
    title="Social Network Engine",
    description="API for social network events management.",
    version="1.0.0",
    lifespan=lifespan,
)

prefix = "/api/v1"

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix=prefix)
app.include_router(groupes.router, prefix=prefix)
app.include_router(events.router, prefix=prefix)
app.include_router(discussions.router, prefix=prefix)
app.include_router(albums.router, prefix=prefix)
app.include_router(sondages.router, prefix=prefix)
app.include_router(billetteries.router, prefix=prefix)
app.include_router(shopping_list.router, prefix=prefix)
app.include_router(covoiturages.router, prefix=prefix)
