from elasticsearch import Elasticsearch, helpers
from dotenv import load_dotenv
import os
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import requests

app = Flask(__name__)

load_dotenv()

CLOUD_ENDPOINT = os.getenv("CLOUD_ENDPOINT")
API_KEY = os.getenv("API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

index_prefix = "podcast_"

# Elasticsearch client
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

# Get Token for Spotify API (valid for 1h)
response = requests.post("https://accounts.spotify.com/api/token", data={"grant_type": "client_credentials", "client_id": SPOTIFY_CLIENT_ID, "client_secret": SPOTIFY_CLIENT_SECRET})
if response.status_code == 404:
    print("Could not get spotify access token.")
    print(response.text)
    exit()

SPOTIFY_ACCESS_TOKEN = response.json()["access_token"]

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
        "episode_description": episode_info[8],
        "duration": episode_info[9],
      }
  return metadata

metadata = read_metadata()

@app.route('/search')
@cross_origin(origin='*')
def search():
    search_query = request.args.get('q')
    clip_length = request.args.get('length')
    print(search_query)
    print(clip_length)
    print("Searching for: " + search_query + " in " + clip_length + " clips")
    search_result = client.search(index=index_prefix + clip_length, query={"match": {"transcript_text": search_query}}, _source={"includes": ["show_id", "episode_id", "transcript_text", "start_time", "end_time"]}, size=10)
    hits = search_result["hits"]["hits"]

    # Map all hits from the same show and episode to the same dictionary
    episode_map = {}
    episode_ids = []
    for hit in hits:
        episode_id = hit["_source"]["episode_id"]
        if episode_id in metadata:
            episode_ids.append(episode_id)
            
            if episode_id not in episode_map:
                episode_map[episode_id] = {
                    "show_id": hit["_source"]["show_id"],
                    "episode_id": episode_id,
                    "show_name": metadata[episode_id]["show_name"],
                    "show_description": metadata[episode_id]["show_description"],
                    "publisher": metadata[episode_id]["publisher"],
                    "episode_name": metadata[episode_id]["episode_name"],
                    "episode_description": metadata[episode_id]["episode_description"],
                    "language": metadata[episode_id]["language"],
                    "rss_link": metadata[episode_id]["rss_link"],
                    "duration": metadata[episode_id]["duration"],
                    "snippets": []
                }
                
            snippet = {
                "transcript_text": hit["_source"]["transcript_text"],
                "start_time": hit["_source"]["start_time"],
                "end_time": hit["_source"]["end_time"],
                "score": hit["_score"],
            }
            episode_map[episode_id]["snippets"].append(snippet)
        
    # Get Spotify episodes for each episode_id (get picture uri)
    if len(episode_ids) > 0:
        episodes_response = requests.get("https://api.spotify.com/v1/episodes?market=SE&ids=" + ",".join(episode_ids), headers={"Authorization": "Bearer " + SPOTIFY_ACCESS_TOKEN})
        if episodes_response.status_code == 404:
            print("Could not get spotify episodes.")
            print(episodes_response.text)
            exit()
        
        episodes = episodes_response.json()["episodes"]
        for episode in episodes:
            if episode is None:
                continue
            
            episode_id = episode["id"]
            if episode_id in episode_map:
                episode_map[episode_id]["picture_uri"] = episode["images"][1]["url"]
                episode_map[episode_id]["release_date"] = episode["release_date"]
                episode_map[episode_id]["duration_ms"] = episode["duration_ms"]
    
    formatted_results = { "episodes": []}
    for episode_id, episode in episode_map.items():
        formatted_results["episodes"].append(episode)
    
    response = jsonify(formatted_results)
    # response.headers.add("Access-Control-Allow-Origin", "*")
    # response.headers.add("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept")
    return response