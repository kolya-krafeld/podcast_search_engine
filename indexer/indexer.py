from elasticsearch import Elasticsearch, helpers
import os
import json
from dotenv import load_dotenv
import time

load_dotenv()

start_time_program = time.time()

CLOUD_ENDPOINT = os.getenv("CLOUD_ENDPOINT")
API_KEY = os.getenv("API_KEY")


client = Elasticsearch(
  CLOUD_ENDPOINT, 
  API_KEY
)

folder_path = "./data/podcast-transcripts"
index_name = "podcast"

# TODO: 1. make sure that when adding the same document twice, it only gets added once - A solution could be to generate an ID for the documents - MELI

# Check if the index already exists
if not client.indices.exists(index=index_name):
    # Create the index with specific settings
    client.indices.create(
        index=index_name,
        body={
            "settings": {"index": {"number_of_shards": 3, "number_of_replicas": 0}},
            "mappings": {
                "properties": {
                    "show_id": {"type": "keyword", "index": False},
                    "episode_id": {"type": "keyword", "index": False},
                    "transcript_text": {"type": "text", "index": True},
                    "start_time": {"type": "float", "index": False},
                    "end_time": {"type": "float", "index": False}
                }
            },
        },
    )

transcript_snippets = []

# TODO 2: check size podcast: if the size is less than half, merge it with previous one. If it's bigger then we make a new document. 

# TODO 3: given a time, generate the documents 
# 30s, 2 minutes, 5minutes, 

# TODO 4: modify code so that it allows to do the overlap window of 30 seconds - MELI 
for root, dirs, files in os.walk(folder_path):
    # Loop over all json files in the folder
    for file_name in files:
        if file_name.endswith(".json"):
            show_id = root.split("/")[-1].split("show_")[-1]
            episode_id = file_name.split(".json")[0]
            with open(os.path.join(root, file_name)) as f:
                # Read content of file
                json_data = json.load(f)

                # Loop over array elements in results
                for result in json_data["results"]:
                    # Extract the transcript text
                    alternative = result["alternatives"][0]
                    if "transcript" in alternative:
                        transcript_text = alternative["transcript"]

                        # Get start time of first word and end time of last word - is in seconds -> Remove the 's' at the end
                        start_time = float(alternative["words"][0]["startTime"][:-1])
                        end_time = float(alternative["words"][-1]["endTime"][:-1])

                        # Append the transcript snippet to the list
                        snippet = {
                            "show_id": show_id,
                            "episode_id": episode_id,
                            "transcript_text": transcript_text,
                            "start_time": start_time,
                            "end_time": end_time,
                        }
                        transcript_snippets.append(snippet)
     
                        if len(transcript_snippets) >= 50000:
                            helpers.bulk(client, transcript_snippets, index=index_name)
                            print('Bulk done')
                            transcript_snippets = []
       


# Upload the remaining transcript snippets to Elasticsearch
helpers.bulk(client, transcript_snippets, index=index_name)

total_duration = time.time() - start_time_program

print(f"Indexing Duration: {round(total_duration)} seconds")
