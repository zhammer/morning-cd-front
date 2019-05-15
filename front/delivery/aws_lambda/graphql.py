import json
import os
from typing import Dict

from aws_xray_sdk.core import patch

from graphql.error.located_error import GraphQLLocatedError

import graphql_server

import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration
from sentry_sdk.integrations.logging import ignore_logger

from front.definitions import exceptions
from front.delivery.aws_lambda import util
from front.delivery.graphql import schema


if os.environ.get('AWS_EXECUTION_ENV'):
    # setup sentry
    sentry_sdk.init(
        dsn='https://8f452b81ea4e4f188559a678cb0114fb@sentry.io/1358957',
        integrations=[AwsLambdaIntegration()]
    )
    ignore_logger('graphql.execution.executor')
    ignore_logger('graphql.execution.utils')

    # setup xray patching
    libraries = ('requests', 'boto3', 'botocore')
    patch(libraries)


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

    for error in (results[0].errors or []):
        if isinstance(error, GraphQLLocatedError):
            if not isinstance(error.original_error, exceptions.FrontException):
                raise error.original_error

    # if _from_graphql_playground(event):
    #     access_control_allow_origin = 'https://www.graphqlbin.com'
    # else:
    #     access_control_allow_origin = os.environ.get('ACCESS_CONTROL_ALLOW_ORIGIN', '*')

    return {
        'statusCode': 200,
        'body': json.dumps(results[0].to_dict()),
        'headers': {
            'Access-Control-Allow-Origin': '*'
        }
    }


def _from_graphql_playground(event: Dict) -> bool:
    try:
        origin: str = event['headers']['origin']
    except (KeyError, ValueError):
        return False

    return origin == 'https://www.graphqlbin.com'
