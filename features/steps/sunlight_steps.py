import json
import os
from contextlib import contextmanager

import behave
from behave import given, then, when

from faaspact_maker import Interaction, PactMaker, RequestWithMatchers, ResponseWithMatchers

import responses

from features.fixtures.spotify import make_post_client_credentials
from features.support.make_graphql_request import make_graphql_request

from front.delivery.aws_lambda.graphql import handler as front_graphql_handler


@given('sunrise is at "{sunrise_utc}" utc')  # noqa: F811
def step_impl(context, sunrise_utc: str):
    context.sunrise_utc = sunrise_utc


@given('sunset is at "{sunset_utc}" utc')  # noqa: F811
def step_impl(context, sunset_utc: str):
    context.sunset_utc = sunset_utc


@when('I request today\'s sunlight window')  # noqa: F811
def step_impl(context):
    query = """
    query sunlight($ianaTimezone: String!, $onDate: Date!) {
      sunlightWindow(ianaTimezone: $ianaTimezone, onDate: $onDate) {
        sunriseUtc
        sunsetUtc
      }
    }
    """
    variables = {
        'ianaTimezone': context.iana_timezone,
        'onDate': context.todays_date.isoformat()
    }

    event = make_graphql_request(query, variables)

    with sunlight_service_mock_network(context) as mock_network:
        fetch_sunlight_window_response = front_graphql_handler(event, {})

    context.response = fetch_sunlight_window_response
    context.mock_network = mock_network


@then('I get a sunlight window with the values')  # noqa: F811
def step_impl(context):
    expected_sunrise_utc = context.table[0][0]
    expected_sunset_utc = context.table[0][1]

    expected_sunlight_window_response = {
        'data': {
            'sunlightWindow': {
                'sunriseUtc': expected_sunrise_utc,
                'sunsetUtc': expected_sunset_utc
            }
        }
    }

    body = json.loads(context.response['body'])
    assert body == expected_sunlight_window_response


@contextmanager
def sunlight_service_mock_network(context: behave.runner.Context):
    pact_dir = os.environ.get('PACT_DIRECTORY', 'pacts')
    pact = PactMaker('front', 'sunlight', 'https://micro.morningcd.com', pact_directory=pact_dir)
    pact.add_interaction(Interaction(
        description='a request for ga sunlight window',
        request=RequestWithMatchers(
            method='GET',
            path='/sunlight',
            query={
                'iana_timezone': [context.iana_timezone],
                'on_date': [context.todays_date.isoformat()]
            }
        ),
        response=ResponseWithMatchers(
            status=200,
            body={
                'sunrise_utc': context.sunrise_utc,
                'sunset_utc': context.sunset_utc
            }
        )
    ))

    with responses.RequestsMock() as mock_responses:
        # spotify gateway eagerly fetches client credentials on creation
        mock_responses.add(
            make_post_client_credentials()
        )

        # we check the date
        with pact.start_mocking(outer=mock_responses):
            yield mock_responses
