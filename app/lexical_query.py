def build_es_query(query_context, query_type, search_field):
    query = {
        "query": {
            "bool": {}
        }
    }

    if query_type == "intersection":
        # Intersection query: all terms must appear, position does not matter
        terms = query_context.split()
        query['query']['bool']['must'] = [
            {"match": {search_field: term}} for term in terms
        ]

    elif query_type == "phrase":
        # Phrase query: exact phrase must appear in the given order
        query['query']['bool']['must'] = [
            {"match_phrase": {search_field: query_context}}
        ]

    elif query_type == "wildcard":
        # Wildcard query: process each word for potential wildcards
        terms = query_context.split()
        should_conditions = []
        for term in terms:
            if "*" in term or "?" in term:
                should_conditions.append({"wildcard": {search_field: term}})
            else:
                should_conditions.append({"match": {search_field: term}})
        query['query']['bool']['should'] = should_conditions
        query['query']['bool']['minimum_should_match'] = 1

    return query
