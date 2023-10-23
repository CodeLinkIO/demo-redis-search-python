import datetime
import json
import os
from typing import Union
from dotenv import load_dotenv
from redis import Redis
from redis.commands.json.path import Path
from pydantic import BaseModel
from slugify import slugify

load_dotenv()


class Article(BaseModel):
    id: str
    title: str
    url: str
    category: str
    description: str
    date: Union[str, datetime.datetime, int]
    authors: str

    class Config:
        json_encoders = {datetime.datetime: lambda v: int(v.timestamp())}


redis_client = Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    password=os.environ.get("REDIS_PASSWORD"),
)

DATA_PATH = "data/News_Category_Dataset_v3.json"

with open(DATA_PATH, "r") as f:
    for line in f:
        data = json.loads(line)
        id = slugify(data["title"])
        data["id"] = id
        data["date"] = datetime.datetime.strptime(data["date"], "%Y-%m-%d")
        article = Article(**data)
        print(f"> Importing article {article.title}")
        redis_client.json().set(
            f"articles:{article.id}", Path.rootPath(), article.json()
        )
