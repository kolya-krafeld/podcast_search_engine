from elasticsearch import Elasticsearch
from langchain.output_parsers.json import SimpleJsonOutputParser
from langchain_community.chat_models import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel

from elastic_index_info import get_indices_infos
from prompts import DSL_PROMPT

import json

with open("../config.json") as config_file:
    config = json.load(config_file)

# test cloud
# CLOUD_ID = config["lee_cloud"]["Cloud_id"]
# API_KEY = config["lee_cloud"]["API_KEY"]
#
# db = Elasticsearch(
#     cloud_id=CLOUD_ID,
#     api_key=API_KEY
# )
# INCLUDE_INDICES = ["lee_test_1"]

# public cloud
CLOUD_ID = config["public_cloud"]["Cloud_id"]
API_KEY = config["public_cloud"]["API_KEY"]

db = Elasticsearch(
    cloud_id=CLOUD_ID,
    api_key=API_KEY
)

# Specify indices to include
INCLUDE_INDICES = ["podcast_30"]

# With the Elasticsearch connection created, we can now move on to the chain
OPENAI_API_KEY = config["OPENAI"]["OPENAI_API_KEY"]
_model = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)

chain = (
        {
            "input": lambda x: x["input"],
            "indices_info": lambda _: get_indices_infos(db, include_indices=INCLUDE_INDICES),
            "top_k": lambda x: x.get("top_k", 10),
        }
        | DSL_PROMPT
        | _model
        | SimpleJsonOutputParser()
)


class ChainInputs(BaseModel):
    input: str
    top_k: int = 10


chain = chain.with_types(input_type=ChainInputs)
