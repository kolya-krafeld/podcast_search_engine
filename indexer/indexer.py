from elasticsearch import Elasticsearch, helpers
import os
import json
import hashlib
import time
from dotenv import load_dotenv

class PodcastTranscriptIndexer:
    def __init__(self, cloud_endpoint, api_key, folder_path, index_name):
        self.client = Elasticsearch(cloud_endpoint, api_key=api_key)
        self.folder_path = folder_path
        self.index_name = index_name

    def ensure_index_exists(self):
        if not self.client.indices.exists(index=self.index_name):
            # Create the index with specific settings
            self.client.indices.create(
                index=self.index_name,
                body={
                    "settings": {
                        "index": {"number_of_shards": 3, "number_of_replicas": 0}
                    },
                    "mappings": {
                        "properties": {
                            "show_id": {"type": "keyword", "index": False},
                            "episode_id": {"type": "keyword", "index": False},
                            "transcript_text": {"type": "text", "index": True},
                            "start_time": {"type": "float", "index": False},
                            "end_time": {"type": "float", "index": False},
                        }
                    },
                },
            )

    @staticmethod
    def generate_unique_id(show_id, episode_id, start_time, end_time):
        unique_string = f"{show_id}_{episode_id}_{start_time}_{end_time}"
        return hashlib.sha256(unique_string.encode("utf-8")).hexdigest()

    def process_files(self, size_batch, document_size=30):
        transcript_snippets = []
        for root, dirs, files in os.walk(self.folder_path):
            # Loop over all json files in the folder
            for file_name in files:
                if file_name.endswith(".json"):
                    with open(os.path.join(root, file_name)) as f:
                        # Read content of file
                        json_data = json.load(f)
                        self.process_document(
                            json_data,
                            transcript_snippets,
                            root,
                            file_name,
                            document_size,
                        )

                        if len(transcript_snippets) >= size_batch:
                            self.bulk_upload_documents(transcript_snippets)
                            transcript_snippets = []

        # Upload any remaining documents
        if len(transcript_snippets) > 0:
            self.bulk_upload_documents(transcript_snippets)
    
    def append_snippets(self, transcript_snippets, show_id, episode_id, doc_start_time, doc_end_time, doc_transcript_text):
        unique_id = self.generate_unique_id(
            show_id, episode_id, doc_start_time, doc_end_time
        )

        # Append the transcript snippet to the list
        snippet = {
            "_id": unique_id,
            "show_id": show_id,
            "episode_id": episode_id,
            "transcript_text": doc_transcript_text,
            "start_time": doc_start_time,
            "end_time": doc_end_time,
        }
        transcript_snippets.append(snippet)

    def process_document(self, json_data, transcript_snippets, root, file_name, document_size):

        # given a document_size, generate the documents --> 30s, 2 minutes, 5minutes 
        doc_start_time = 0
        doc_end_time = 0
        doc_transcript_text = ""
        doc_cur_size = 0

        show_id = root.split("/")[-1].split("show_")[-1]
        episode_id = file_name.split(".json")[0]

        # Loop over array elements in results
        for result in json_data["results"]:
             # Extract the transcript text
            alternative = result["alternatives"][0]
            if "transcript" in alternative:
                transcript_text = alternative["transcript"]

                # Get start time of first word and end time of last word - is in seconds -> Remove the 's' at the end
                start_time = float(alternative["words"][0]["startTime"][:-1])
                end_time = float(alternative["words"][-1]["endTime"][:-1])
                time_len = end_time - start_time

                if doc_transcript_text == "":
                    doc_start_time = start_time
                
                # generate and append to the list when the gap increases
                if abs(document_size - doc_cur_size) < abs(document_size - doc_cur_size - time_len):
                    # check size podcast: if the size is less than half, merge it with previous one. If it's bigger then we make a new document. 
                    if time_len <= 15:
                        doc_transcript_text += transcript_text
                        # extend the end time
                        doc_end_time = end_time

                    self.append_snippets(transcript_snippets, show_id, episode_id, doc_start_time, doc_end_time, doc_transcript_text)                    
                    
                    if time_len <= 15:
                        #generate a new document next transcript
                        doc_transcript_text = ""
                        doc_cur_size = 0
                    else:
                        #generate a new document now
                        doc_transcript_text = transcript_text
                        doc_cur_size = time_len
                        doc_start_time = start_time
                else:
                    doc_transcript_text += transcript_text
                    doc_cur_size += time_len    
                
                # keep the last end time as the document end time
                doc_end_time = end_time

        #if the remaining snippets cannot reach document size, still generate a document and append
        if doc_transcript_text != "":
            self.append_snippets(transcript_snippets, show_id, episode_id, doc_start_time, doc_end_time, doc_transcript_text)
                
    def bulk_upload_documents(self, documents):
        helpers.bulk(self.client, documents, index=self.index_name)
        print("Bulk upload done")


if __name__ == "__main__":
    load_dotenv()
    start_time_program = time.time()

    CLOUD_ENDPOINT = os.getenv("CLOUD_ENDPOINT")
    API_KEY = os.getenv("API_KEY")
    folder_path = "../data/testing_tianning"
    index_name = "testing_ning_300_version2"
    size_batch = 50000

    indexer = PodcastTranscriptIndexer(CLOUD_ENDPOINT, API_KEY, folder_path, index_name)
    indexer.ensure_index_exists()
    indexer.process_files(size_batch, document_size=300)

    total_duration = time.time() - start_time_program
    print(f"Indexing Duration: {round(total_duration)} seconds")
