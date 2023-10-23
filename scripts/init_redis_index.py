import os

from dotenv import load_dotenv
from redis import Redis
from redis.commands.search.field import NumericField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType

load_dotenv()

redis_client = Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    password=os.environ.get("REDIS_PASSWORD"),
)

# redis_client.ft("articles").dropindex()

schema = (
    TextField("$.title", as_name="title", weight=10.0),
    TextField("$.description", as_name="description"),
    NumericField("$.date", as_name="date"),
    TextField("$.category", as_name="category"),
)

redis_client.ft("articles").create_index(
    schema, definition=IndexDefinition(prefix=["articles:"], index_type=IndexType.JSON)
)
