from collections.abc import Sequence

from beanie import Document, init_beanie
from pymongo import AsyncMongoClient

from src.config import settings


async def init_db(
    document_models: Sequence[type[Document]],
) -> AsyncMongoClient:
    client = AsyncMongoClient(settings.mongo_uri)
    await init_beanie(
        database=client[settings.mongo_db_name],
        document_models=list(document_models),
    )

    return client
