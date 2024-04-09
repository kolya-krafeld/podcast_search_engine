from elasticsearch import Elasticsearch, helpers
from dotenv import load_dotenv
import os

load_dotenv()

ELASTIC_PASSWORD = os.getenv("ES_PASSWORD")

client = Elasticsearch(
  "https://localhost:9200",
  ca_certs="./http_ca.crt",
  basic_auth=("elastic", ELASTIC_PASSWORD)
)

print(client.search(index="podcast_tests", q="snow"))