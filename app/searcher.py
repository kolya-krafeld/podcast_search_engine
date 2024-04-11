from elasticsearch import Elasticsearch, helpers
from dotenv import load_dotenv
import os

load_dotenv()

CLOUD_ENDPOINT = os.getenv("CLOUD_ENDPOINT")
API_KEY = os.getenv("API_KEY")

index_name = "podcast"

client = Elasticsearch(
  CLOUD_ENDPOINT, 
  API_KEY
)

client = Elasticsearch(
  CLOUD_ENDPOINT, 
  API_KEY
)

query = {
    "query": {
        "match": {
            "transcript_text": {
                "query": "green grass",
                "operator": "and"
            }
        }
    }
}

print(client.search(index= index_name, body=query))
