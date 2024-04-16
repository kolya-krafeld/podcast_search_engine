from elastic_query_generator.chain import chain
import json
import ast

if __name__ == "__main__":
    inpt = chain.invoke({"input": "give me some podcasts that talks about sex and life"})
    print(inpt)  # noqa: T201
    print("\n")
    query = json.dumps(inpt)
    print(query)  # noqa: T201
