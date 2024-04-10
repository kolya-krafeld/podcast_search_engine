indexPodcast = {
    "properties":{
        "show_id":{
            "type": "keyword" 
        },
        "episode_id":{
            "type": "keyword"
        },
         "transcript_text":{
            "type": "text",
            "index": True
        },
         "start_time":{
            "type": "float"
        },
         "end_time":{
            "type": "float"
        }
    }
}