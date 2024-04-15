from elastic_query_generator.chain import chain

if __name__ == "__main__":
    print(chain.invoke({"input": "fetch all the customers that may be a women"}))  # noqa: T201