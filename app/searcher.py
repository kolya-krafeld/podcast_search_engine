from elasticsearch import Elasticsearch, helpers
from dotenv import load_dotenv
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

load_dotenv()

CLOUD_ENDPOINT = os.getenv("CLOUD_ENDPOINT")
API_KEY = os.getenv("API_KEY")

index_name = "podcast"

client = Elasticsearch(
  CLOUD_ENDPOINT, 
  api_key = API_KEY
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

# Read metadata.tsv file
# Returns map of episode_filename_prefix to metadata
def read_metadata():
  metadata = {}
  with open("../data/metadata.tsv", "r") as file:
    lines = file.readlines()
    for line in lines:
      episode_info = line.strip().split("\t")
      episode_filename_prefix = episode_info[-1]
      metadata[episode_filename_prefix] = {
        "show_name": episode_info[1],
        "show_description": episode_info[2],
        "publisher": episode_info[3],
        "language": episode_info[4],
        "rss_link": episode_info[5],
        "episode_uri": episode_info[6],
        "episode_name": episode_info[7],
        "episode_description": episode_info[8]
      }
  return metadata

metadata = read_metadata()

# Turns results dic into list of dictionaries that can be returned as JSON
def format_results(results):
    formatted_results = {"episodes": []}
    for show_id, episodes in results.items():
        show = {
            "show_id": show_id,
            "show_name": episodes["show_name"],
            "show_description": episodes["show_description"],
            "publisher": episodes["publisher"]
        }
        for episode_id, snippets in episodes.items():
            if episode_id not in ["show_name", "show_description", "publisher"]:
                episode = {
                    "episode_id": episode_id,
                    "episode_name": snippets[0]["episode_name"],
                    "episode_description": snippets[0]["episode_description"],
                    "language": snippets[0]["language"],
                    "rss_link": snippets[0]["rss_link"],
                    "transcript_snippets": snippets,
                    "show": show
                }
                formatted_results["episodes"].append(episode)
    return formatted_results

@app.route('/search')
def get_incomes():
    search_query = request.args.get('q')
    search_result = client.search(index=index_name, query={"match": {"transcript_text": search_query}}, _source={"includes": ["show_id", "episode_id", "transcript_text", "start_time", "end_time"]}, size=10)
    hits = search_result["hits"]["hits"]

    # Map all hits from the same show and episode to the same dictionary
    episode_map = {}
    for hit in hits:
        show_id = hit["_source"]["show_id"]
        episode_id = hit["_source"]["episode_id"]
        
        if episode_id not in episode_map:
            episode_map[episode_id] = {
                "show_name": metadata[episode_id]["show_name"],
                "show_description": metadata[episode_id]["show_description"],
                "publisher": metadata[episode_id]["publisher"],
                "episode_name": metadata[episode_id]["episode_name"],
                "episode_description": metadata[episode_id]["episode_description"],
                "language": metadata[episode_id]["language"],
                "rss_link": metadata[episode_id]["rss_link"],
                "snippets": []
            }
            
        snippet = {
            "transcript_text": hit["_source"]["transcript_text"],
            "start_time": hit["_source"]["start_time"],
            "end_time": hit["_source"]["end_time"],
            "score": hit["_score"],
        }
        episode_map[episode_id]["snippets"].append(snippet)
    
    formatted_results = { "episodes": []}
    for episode_id, episode in episode_map.items():
        formatted_results["episodes"].append(episode)
    
    response = jsonify(formatted_results)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response