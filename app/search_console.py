from elasticsearch import Elasticsearch
import json

with open("../config.json") as config_file:
    config = json.load(config_file)

CLOUD_ID = config["lee_cloud"]["Cloud_id"]
API_KEY = config["lee_cloud"]["API_KEY"]

es = Elasticsearch(
    cloud_id=CLOUD_ID,
    api_key=API_KEY
)


def search_index(index_name, query):
    """
    Search an index with a specified query.

    Args:
    index_name (str): Name of the index to search.
    query (dict): A dictionary representing the Elasticsearch query.

    Returns:
    dict: The search results returned by Elasticsearch.
    """
    try:
        # Perform the search
        response = es.search(index=index_name, body=query)
        return response
    except Exception as e:
        print("Error in search:", e)
        return None


# Example usage:
if __name__ == "__main__":
    index_name = "lee_test_1"  # replace with your index name
    query = {
        "query": {
            "match_all": {

            }
        }
    }
    result = search_index(index_name, query)
    print(result)
