def build_es_query(query_string, search_field):
    query = {
        "query": {
            "bool": {}
        }
    }

    # Check for exact phrase (enclosed in quotation marks)
    if query_string.startswith('"') and query_string.endswith('"'):
        query_context = query_string[1:-1]  # Remove the quotation marks
        query_type = "phrase"
    else:
        query_context = query_string
        query_type = "intersection"

    terms = query_context.split()

    # Check if any term contains a wildcard
    contains_wildcard = any("*" in term or "?" in term for term in terms)

    if contains_wildcard:
        # Wildcard search: each term is processed for potential wildcards
        should_conditions = []
        for term in terms:
            if "*" in term or "?" in term:
                should_conditions.append({"wildcard": {search_field: term}})
            else:
                should_conditions.append({"match": {search_field: term}})
        query['query']['bool']['should'] = should_conditions
        query['query']['bool']['minimum_should_match'] = 1
    elif query_type == "phrase":
        # Phrase query: exact phrase must appear in the given order
        query['query']['bool']['must'] = [
            {"match_phrase": {search_field: query_context}}
        ]
    elif query_type == "intersection":
        # Intersection query: all terms must appear, position does not matter
        query['query']['bool']['must'] = [
            {"match": {search_field: term}} for term in terms
        ]

    return query
