# Python Middleware

I used Flask to generate a simple middleware endpoint. Run it by running:
````
flask --app searcher run
````

Install flask with `pip install Flask`.

For the LangChain application, setting the environment:

`pip install -U langchain-cli`
or
`pip3 install -U langchain-cli`

When using the LangChain feature, make sure the correct elastic client is connected both in searcher.py and in chain.py.

Chain.py will search for an example to let the agent know the template of the query, e.g field, etc.