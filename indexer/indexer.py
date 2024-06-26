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
                        if self.allow_overlap:
                            self.process_document_overlap(json_data, transcript_snippets, root, file_name)
                        else:
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
                # initiate the time
                doc_start_time = start_time
                doc_end_time = end_time

            doc_cur_size = doc_end_time - doc_start_time
            # generate and append to the list when the gap increases
            if abs(self.document_size - doc_cur_size) < abs(self.document_size - doc_cur_size - time_len):
                # check size podcast: if the size is less than half, merge it with previous one. 
                # If it's bigger then we make a new document.
                if time_len <= 15:
                    doc_transcript_text += transcript_text
                    # extend the end time
                    doc_end_time = end_time

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
                else:
                    # generate a new document now
                    doc_transcript_text = transcript_text
                    doc_start_time = start_time
            else:
                doc_transcript_text += transcript_text

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
    
    def process_document_overlap(self, json_data, transcript_snippets, root, file_name):
        """Processes each JSON document to extract transcript snippets based on the specified document size with different start timing.

        Args:
            json_data (dict): The JSON data extracted from a transcript file.
            transcript_snippets (list): A list of transcript snippets to which new snippets will be added.
            root (str): The root directory path where the JSON file is located.
            file_name (str): The name of the JSON file being processed.

        """
        #keep two sliding windows, one for start time, one for transcript text
        doc_start_time_queue = []
        doc_end_time = 0
        doc_transcript_text_queue = []

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

            if doc_transcript_text_queue == []:
                #initiate the window
                doc_end_time = end_time
                doc_transcript_text_queue.append(transcript_text)
                doc_start_time_queue.append(start_time)
                continue

            doc_cur_size = doc_end_time - doc_start_time_queue[0]
            # generate and append to the list when the gap increases
            if abs(self.document_size - doc_cur_size) < abs(self.document_size - doc_cur_size - time_len):
                # check size podcast: if the size is less than 15, merge it with previous one. 
                if time_len <= 15:
                    doc_start_time_queue.append(start_time)
                    doc_transcript_text_queue.append(transcript_text)
                    doc_end_time = end_time
                
                doc_transcript_text = ''.join(doc_transcript_text_queue)

                self.append_snippets(
                    transcript_snippets,
                    show_id,
                    episode_id,
                    doc_start_time_queue[0],
                    doc_end_time,
                    doc_transcript_text,
                )

                # If it's bigger then we add it later.
                if time_len > 15:
                    doc_end_time = end_time
                    doc_start_time_queue.append(start_time)
                    doc_transcript_text_queue.append(transcript_text)

                doc_cur_size = doc_end_time - doc_start_time_queue[0]
                #remove the begining part until the size of window is smaller than document size
                while doc_start_time_queue != [] and doc_transcript_text_queue != [] and self.document_size < doc_cur_size:
                    #pop the first element in the queue
                    doc_start_time_queue.pop(0)
                    doc_transcript_text_queue.pop(0)
                    doc_cur_size = doc_end_time - doc_start_time_queue[0]
            else:
                doc_start_time_queue.append(start_time)
                doc_transcript_text_queue.append(transcript_text)

            # keep the last end time as the document end time
            doc_end_time = end_time

        # if the remaining snippets cannot reach document size, still generate a document and append
        doc_transcript_text = ''.join(doc_transcript_text_queue)
        if doc_transcript_text != "":
            self.append_snippets(
                transcript_snippets,
                show_id,
                episode_id,
                doc_start_time_queue[0],
                doc_end_time,
                doc_transcript_text,
            )

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
    
    CLOUD_ENDPOINT = os.getenv("CLOUD_ENDPOINT")
    API_KEY = os.getenv("API_KEY")
    folder_path = "data/podcast-transcripts"
    index_name = "podcast_overlap_300"
    size_batch = 50000

    # Parameters to play around for experiments
    allow_overlap = True
    document_size = 300  # time in seconds for documents length

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

    indexer.ensure_index_exists()
    indexer.process_files()

    total_duration = time.time() - start_time_program
    print(f"Indexing Duration: {round(total_duration)} seconds")
