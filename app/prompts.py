from langchain_core.prompts.prompt import PromptTemplate

PROMPT_SUFFIX = """Only use the following Elasticsearch indices:
{indices_info}

Question: {input}
ESQuery:"""

DEFAULT_DSL_TEMPLATE = """Given an input question, create a syntactically correct Elasticsearch query to run. 

Unless told to do not query for all the columns from a specific index, only ask for a the few relevant columns given the question.

Pay attention to use only the column names that you can see in the mapping description. Be careful to not query for columns that do not exist. 

Carefully analyze the question's intention, whether it is a phrase query or just a simple intersection query.

If it is a phrase query, make sure to use the match_phrase query. If it is an intersection query, use the match query.

Also you can use boolean query with flexibility, understand the intention of which terms must appear and which should or should not appear.

Also, pay attention to which column is in which index. Return the query as valid json.

Use the following format:

Question: Question here
ESQuery: Elasticsearch Query formatted as json
"""  # noqa: E501

DSL_PROMPT = PromptTemplate.from_template(DEFAULT_DSL_TEMPLATE + PROMPT_SUFFIX)

# Always limit your query to at most {top_k} results, unless the user specifies in their question a specific number of examples they wish to obtain, or unless its implied that they want to see all.
# You can order the results by a relevant column to return the most interesting examples in the database.
