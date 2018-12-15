import json
from typing import Dict


def make_graphql_request(query: str, variables: Dict) -> Dict[str, str]:
    return {
        'body': json.dumps({
            'query': query,
            'variables': variables
        })
    }
