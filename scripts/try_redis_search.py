import datetime
import json
import os

from dotenv import load_dotenv
from redis import Redis
from redis.commands.json.path import Path
from redis.commands.search.field import NumericField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from redis.commands.search.suggestion import Suggestion

load_dotenv("search/scripts/.env.local")

redis_client = Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    password=os.environ.get("REDIS_PASSWORD"),
)

books = []
titles = [
    "Chuyện Tình Yêu",
    "Cuộc Đời Nhỏ",
    "Ngày Hạnh Phúc",
    "Sứ Mệnh Đại Chiến Covid-19",
    "Tình Yêu Không Thể Nói Covid-12",
    "Hành Trình Đến Thành Công",
    "Tình Bạn Trẻ Tuổi",
    "Chiến Trận Tự Do",
    "Cuộc Đời Lớn",
    "Người Tình Của Tôi",
]
for i in range(10):
    title = titles[i]
    timestamp = datetime.datetime.now().timestamp()
    books.append({"title": title, "date": timestamp})

for index, book in enumerate(books):
    redis_client.json().set(f"books:{book['title']}", Path.rootPath(), book)
    redis_client.ft("books").sugadd("books", Suggestion(book["title"]))

try:
    schema = (
        TextField("$.title", as_name="title"),
        NumericField("$.date", as_name="date"),
    )

    redis_client.ft("books").create_index(
        schema, definition=IndexDefinition(prefix=["books:"], index_type=IndexType.JSON)
    )
except Exception as e:
    print(e)

term = "Ch"
fuzzy_term = "".join([f"%%{w}%%" for w in term.strip().split(" ")])
print(fuzzy_term)
query = bytes("Ch*", "utf-8")
result = redis_client.ft("books").search(Query(query).with_scores())

books = result.docs

for book in books:
    _book = json.loads(book.json)
    score = book.score
    print(f"{_book['title']} - {score}")

result = redis_client.ft("books").sugget("books", term, fuzzy=len(term) > 3, num=10)
print(result)
