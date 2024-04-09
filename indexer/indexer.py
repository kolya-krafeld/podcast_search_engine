from elasticsearch import Elasticsearch, helpers
import os
import json
from dotenv import load_dotenv
import os

load_dotenv()

ELASTIC_PASSWORD = os.getenv("ES_PASSWORD")

client = Elasticsearch(
  "https://localhost:9200",
  ca_certs="../http_ca.crt",
  basic_auth=("elastic", ELASTIC_PASSWORD)
)

folder_path = "../data/podcast-transcripts"

transcript_snippets = []

for root, dirs, files in os.walk(folder_path):
    # Loop over all json files in the folder
    for file_name in files:
        if file_name.endswith(".json"):
            show_id = root.split("/")[-1].split("show_")[-1]
            episode_id = file_name.split(".json")[0]
            print("Show:", show_id)
            print("File:", root, file_name)

            with open(os.path.join(root, file_name)) as f: 
                # Read content of file
                json_data = json.load(f)

                # Loop over array elements in results
                for result in json_data["results"]:
                    # Extract the transcript text
                    alternative = result["alternatives"][0]
                    if "transcript" in alternative:
                        transcript_text = alternative["transcript"]

                        # Get start time of first word and end time of last word
                        start_time = alternative["words"][0]["startTime"]
                        end_time = alternative["words"][-1]["endTime"]

                        # Append the transcript snippet to the list
                        snippet = {
                            "show_id": show_id,
                            "episode_id": episode_id,
                            "transcript_text": transcript_text,
                            "start_time": start_time,
                            "end_time": end_time
                        }
                        transcript_snippets.append(snippet)


# Upload the transcript snippets to Elasticsearch
helpers.bulk(client, transcript_snippets, index='podcast_tests')



