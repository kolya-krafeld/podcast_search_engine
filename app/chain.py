from elasticsearch import Elasticsearch
from langchain.output_parsers.json import SimpleJsonOutputParser
from langchain_community.chat_models import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel

from elastic_index_info import get_indices_infos
from prompts import DSL_PROMPT
import os
from dotenv import load_dotenv

import json

load_dotenv()

CLOUD_ID = os.getenv("CLOUD_ID")
API_KEY = os.getenv("API_KEY")

db = Elasticsearch(
    cloud_id=CLOUD_ID,
    api_key=API_KEY
)

# Specify indices to include
INCLUDE_INDICES = ["podcast_120"]

# With the Elasticsearch connection created, we can now move on to the chain
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
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
