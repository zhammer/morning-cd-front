import json
import os
from typing import Dict

import graphql_server

from front.delivery.aws_lambda import util
from front.delivery.graphql import schema


def handler(event: Dict, context: Dict) -> Dict:
    listens_service_api_key = os.environ['LISTENS_SERVICE_API_KEY']
    sunlight_service_api_key = os.environ['SUNLIGHT_SERVICE_API_KEY']
    spotify_client_id = os.environ['SPOTIFY_CLIENT_ID']
    spotify_client_secret = os.environ['SPOTIFY_CLIENT_SECRET']

    body = event['body']
    query_data = json.loads(body)

    front_context = util.create_default_context(
        listens_service_api_key,
        sunlight_service_api_key,
        spotify_client_id,
        spotify_client_secret
    )

    results, _ = graphql_server.run_http_query(
        schema=schema,
        request_method='post',
        data={},
        query_data=query_data,
        context=front_context
    )

    return {
        'statusCode': 200,
        'body': json.dumps(results[0].to_dict()),
        'headers': {
            'Access-Control-Allow-Origin': os.environ.get('ACCESS_CONTROL_ALLOW_ORIGIN', '*')
        }
    }
