from elasticsearch import Elasticsearch, helpers
import os
import json
import hashlib
import time
from dotenv import load_dotenv


class PodcastTranscriptIndexer:
    """
    Class used to index podcast transcripts into an Elasticsearch index from JSON formatted transcript files.
    """

    def __init__(self, cloud_endpoint, api_key, folder_path, index_name, size_batch, document_size, allow_overlap):
        """Initializes a PodcastTranscriptIndexer instance with parameters to set up Elasticsearch connectivity, 
        indexing preferences, and document processing.

        Args:
            cloud_endpoint (str): The URL of the Elasticsearch cloud service where the index is hosted.
            api_key (str): The API key used for authentication with the Elasticsearch service.
            folder_path (str): The local system path to the folder containing JSON files with podcast transcripts.
            index_name (str): The name of the Elasticsearch index where the transcripts will be stored.
            size_batch (int): The number of transcript snippets to accumulate before performing a bulk upload to Elasticsearch.
            document_size (int): The size in seconds for each document indexed.
            allow_overlap (bool): A flag to enable or disable the inclusion of overlapping text between 2 documents. 
        """
        self.client = Elasticsearch(cloud_id=cloud_endpoint, api_key=api_key)
        self.folder_path = folder_path
        self.index_name = index_name
        self.size_batch = size_batch
        self.document_size = document_size
        self.allow_overlap = allow_overlap

    def ensure_index_exists(self):
        """
        If the Elasticsearch index doesn't exists, create it with specific settings and mappings for storing transcripts.
        """

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
        """Generates a unique SHA-256 hash ID using details of the podcast snippet.

        Args:
            show_id (str): The identifier for the podcast show.
            episode_id (str): The identifier for the specific episode of the podcast.
            start_time (float): The start time of the transcript snippet.
            end_time (float): The end time of the transcript snippet.

        Returns:
            str: A unique SHA-256 hash ID.
        """
        unique_string = f"{show_id}_{episode_id}_{start_time}_{end_time}"
        return hashlib.sha256(unique_string.encode("utf-8")).hexdigest()

    def process_files(self):
        """
        Processes json files from the specified directory, and uploads them in batches to Elasticsearch.
        """
        transcript_snippets = []
        for root, _, files in os.walk(self.folder_path):
            # Loop over all json files in the folder
            for file_name in files:
                if file_name.endswith(".json"):
                    with open(os.path.join(root, file_name)) as f:
                        # Read content of file
                        json_data = json.load(f)
                        self.process_document(json_data, transcript_snippets, root, file_name)
                        if len(transcript_snippets) >= self.size_batch:
                            self.bulk_upload_documents(transcript_snippets)
                            transcript_snippets = []

        # Upload any remaining documents
        if len(transcript_snippets) > 0:
            self.bulk_upload_documents(transcript_snippets)

    def process_document(self, json_data, transcript_snippets, root, file_name):
        """Processes each JSON document to extract transcript snippets based on the specified document size.

        Args:
            json_data (dict): The JSON data extracted from a transcript file.
            transcript_snippets (list): A list of transcript snippets to which new snippets will be added.
            root (str): The root directory path where the JSON file is located.
            file_name (str): The name of the JSON file being processed.

        """
        doc_start_time = 0
        doc_end_time = 0
        doc_transcript_text = ""
        doc_cur_size = 0

        show_id = root.split("/")[-1].split("show_")[-1]
        episode_id = file_name.split(".json")[0]

        # Loop over array elements in results
        for i, result in enumerate(json_data["results"]):
            # Extract the transcript text
            alternative = result["alternatives"][0]

            if "transcript" not in alternative:
                continue

            transcript_text = alternative["transcript"]

            # Get start time of first word and end time of last word - is in seconds -> Remove the 's' at the end
            start_time = float(alternative["words"][0]["startTime"][:-1])
            end_time = float(alternative["words"][-1]["endTime"][:-1])
            time_len = end_time - start_time

            if doc_transcript_text == "":
                doc_start_time = start_time

            # generate and append to the list when the gap increases
            if abs(self.document_size - doc_cur_size) < abs(self.document_size - doc_cur_size - time_len):
                # check size podcast: if the size is less than half, merge it with previous one. 
                # If it's bigger then we make a new document.
                if time_len <= 15:
                    doc_transcript_text += transcript_text
                    # extend the end time
                    doc_end_time = end_time

                if self.allow_overlap:
                    # used to create smoother transitions between transcript snippets by including part of the
                    # following snippet's text and calculating a midpoint time to adjust the end time of the current snippet
                    overlap_text, next_midpoint_time = self.generate_overlap(json_data, i)
                    doc_transcript_text += " " + overlap_text
                    doc_end_time = next_midpoint_time

                self.append_snippets(
                    transcript_snippets,
                    show_id,
                    episode_id,
                    doc_start_time,
                    doc_end_time,
                    doc_transcript_text,
                )

                if time_len <= 15:
                    # generate a new document next transcript
                    doc_transcript_text = ""
                    doc_cur_size = 0
                else:
                    # generate a new document now
                    doc_transcript_text = transcript_text
                    doc_cur_size = time_len
                    doc_start_time = start_time
            else:
                doc_transcript_text += transcript_text
                doc_cur_size += time_len

            # keep the last end time as the document end time
            doc_end_time = end_time

        # if the remaining snippets cannot reach document size, still generate a document and append
        if doc_transcript_text != "":
            self.append_snippets(
                transcript_snippets,
                show_id,
                episode_id,
                doc_start_time,
                doc_end_time,
                doc_transcript_text,
            )

    def generate_overlap(self, json_data, target_pos):
        """Generates an overlapping snippet from the next transcript entry in the dataset.

        Args:
            json_data (dict): The JSON data containing all results for a single podcast episode.
            target_pos (int): The position in the results array that points to the next transcript entry from
            which overlap will be considered.

        Returns:
            tuple: Containing the text for overlap and the midpoint time for the current transcript snippet.
            The first element is a string which is approximately half of the next transcript entry.
            The second element is a float representing the midpoint time of the next transcript entry, used to adjust
            the current snippet's end time.

        """
        # Code is putted in try catch in case there's no next transcript, in that case it returns empty text and time 0
        try:
            next_entry = json_data["results"][target_pos]["alternatives"][0]

            next_transcript_text = next_entry["transcript"]
            next_start_time = float(next_entry["words"][0]["startTime"][:-1])
            next_end_time = float(next_entry["words"][-1]["endTime"][:-1])
            next_time_addition = next_start_time + (next_end_time - next_start_time) / 2

            overlap_text_length = int(len(next_transcript_text) / 2)
            character_check = next_transcript_text[overlap_text_length]
            # Check that the are no splitted words - i.e. that the text finishes in " "
            while character_check != " ":
                overlap_text_length += 1
                character_check = next_transcript_text[overlap_text_length]

            overlap_text = next_transcript_text[:overlap_text_length]
            return overlap_text, next_time_addition
        except Exception:
            return "", 0

    def append_snippets(self, transcript_snippets, show_id, episode_id, doc_start_time, doc_end_time, doc_transcript_text):
        """Appends a transcript snippet to the list of snippets for bulk uploading.

        Args:
            transcript_snippets (list): The list of transcript snippets to be bulk uploaded.
            show_id (str): The show ID of the transcript.
            episode_id (str): The episode ID of the transcript.
            doc_start_time (float): The start time of the transcript snippet.
            doc_end_time (float): The end time of the transcript snippet.
            doc_transcript_text (str): The text of the transcript snippet.
        """
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

    def bulk_upload_documents(self, documents):
        """Uploads a batch of transcript snippets to the Elasticsearch index.

        Args:
            documents (list): A list of documents formatted as dictionary items ready for bulk uploading.
        """
        helpers.bulk(self.client, documents, index=self.index_name)
        print("Bulk upload done.")


if __name__ == "__main__":
    load_dotenv()
    start_time_program = time.time()

    with open("../config.json") as config_file:
        config = json.load(config_file)

    CLOUD_ENDPOINT = config["lee_cloud"]["Cloud_id"]
    API_KEY = config["lee_cloud"]["API_KEY"]
    folder_path = "../data/"
    index_name = "lee_test_1"
    size_batch = 50000

    # Parameters to play around for experiments 
    allow_overlap = True
    document_size = 30  # time in seconds for documents length

    # Initialice and upload documents to Index
    indexer = PodcastTranscriptIndexer(
        CLOUD_ENDPOINT,
        API_KEY,
        folder_path,
        index_name,
        size_batch,
        document_size,
        allow_overlap,
    )
    # indexer.ensure_index_exists()
    # indexer.process_files()

    total_duration = time.time() - start_time_program
    print(f"Indexing Duration: {round(total_duration)} seconds")
