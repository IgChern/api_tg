import redis.asyncio as redis
import json
import uvicorn
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import APIRouter, FastAPI, Query
from envparse import Env
from fastapi.routing import APIRoute
from starlette.requests import Request
from .models import Message

env = Env()
MONGODB_URL = env.str("MONGODB_URL", default="mongodb://mongo_db/test_database")
REDIS_URL = env.str("REDIS_URL", default="redis://redis:6379")
REDIS_CACHE_KEY = env.str("REDIS_CACHE_KEY", default="cached")

client = AsyncIOMotorClient(MONGODB_URL)
app = FastAPI()
app.state.mongo_client = client
app.state.redis = redis.from_url(REDIS_URL)


async def create_record(request: Request, message: Message) -> dict:
    mongo_client: AsyncIOMotorClient = request.app.state.mongo_client["test_database"]
    await mongo_client.records.insert_one(
        {"user_name": message.author, "content": message.text}
    )
    await request.app.state.redis.delete(REDIS_CACHE_KEY)
    return {"Success": True}


async def get_records(
    request: Request, page: int = Query(1, gt=0), size: int = Query(10, gt=0)
) -> dict:
    redis = request.app.state.redis

    cached_messages = await redis.get(REDIS_CACHE_KEY)
    if cached_messages:
        res = json.loads(cached_messages)
    else:

        mongo_client: AsyncIOMotorClient = request.app.state.mongo_client[
            "test_database"
        ]
        cursor = mongo_client.records.find({}, projection={"_id": False})
        res = []
        for document in await cursor.to_list(length=100):
            res.append(document)
        await redis.set(REDIS_CACHE_KEY, json.dumps(res), ex=120)

    start_index = (page - 1) * size
    end_index = start_index + size
    paginated = res[start_index:end_index]

    return {"page": page, "size": size, "result": paginated}


routes = [
    APIRoute(path="/api/v1/message/", endpoint=create_record, methods=["POST"]),
    APIRoute(path="/api/v1/messages/", endpoint=get_records, methods=["GET"]),
]

app.include_router(APIRouter(routes=routes))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
