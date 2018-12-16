import json
from contextlib import contextmanager
from typing import List

from behave import given, then, when

import responses

from features.fixtures.listens_service import (
    make_post_listen_request_day,
    make_post_listen_request_night
)
from features.fixtures.spotify import (
    WHISPERS_SPOTIFY_TRACK,
    make_get_track_whispers_request,
    make_post_client_credentials
)
from features.support.make_graphql_request import make_graphql_request

from front.delivery.aws_lambda.graphql import handler as front_graphql_handler


@given('the first song I listened to today was \'Whispers\' by DAP The Contract')  # noqa: F811
def step_impl(context):
    context.song_id = '4rNGLh1y5Kkvr4bT28yfHU'
    context.using_invalid_id = False


@given('I write the note "{note}"')  # noqa: F811
def step_impl(context, note):
    context.note = note


@when('I submit my listen to morning.cd')  # noqa: F811
def step_impl(context):
    mutation = """
      mutation submit($listenInput: ListenInput!) {
        submitListen(input: $listenInput) {
          id
          listenerName
          listenTimeUtc
          note
          ianaTimezone
          song {
            id
            name
            artistName
            albumName
            imageLargeUrl
            imageMediumUrl
            imageSmallUrl
          }
        }
      }
    """
    variables = {
        'listenInput': {
            'songId': context.song_id,
            'listenerName': context.name,
            'note': context.note,
            'ianaTimezone': context.iana_timezone
        }
    }

    event = make_graphql_request(mutation, variables)

    with submit_listen_mock_network(context) as mock_network:
        submit_listen_response = front_graphql_handler(event, {})
        context.mock_network_calls = steal_mock_calls(mock_network)

    context.response = submit_listen_response


@then('I get a response with my listen from morning.cd')  # noqa: F811
def step_impl(context):
    assert context.response['statusCode'] == 200

    expected_json_body = {
        'data': {
            'submitListen': {
                'ianaTimezone': context.iana_timezone,
                'id': '1',  # first song in db
                'listenTimeUtc': '2018-11-12T15:30:00',
                'listenerName': context.name,
                'note': context.note,
                'song': {
                    'albumName': WHISPERS_SPOTIFY_TRACK['album']['name'],
                    'artistName': WHISPERS_SPOTIFY_TRACK['artists'][0]['name'],
                    'id': context.song_id,
                    'imageLargeUrl': WHISPERS_SPOTIFY_TRACK['album']['images'][0]['url'],
                    'imageMediumUrl': WHISPERS_SPOTIFY_TRACK['album']['images'][1]['url'],
                    'imageSmallUrl': WHISPERS_SPOTIFY_TRACK['album']['images'][2]['url'],
                    'name': WHISPERS_SPOTIFY_TRACK['name']
                }
            }
        }
    }

    body = json.loads(context.response['body'])
    assert body == expected_json_body


@then('a request is sent to the listens service to add my listen')  # noqa: F811
def step_impl(context):
    listens_service_call = context.mock_network_calls[1]

    expected_request_body = {
        'song_id': context.song_id,
        'song_provider': 'SPOTIFY',
        'listener_name': context.name,
        'iana_timezone': context.iana_timezone,
        'note': context.note
    }

    actual_request_body = json.loads(listens_service_call.request.body)
    assert actual_request_body == expected_request_body


@then('I get an error response that says "{error_message}"')  # noqa: F811
def step_impl(context, error_message):
    assert context.response['statusCode'] == 200

    body = json.loads(context.response['body'])
    assert error_message in body['errors'][0]['message']


def steal_mock_calls(mock_network: responses.RequestsMock) -> List[responses.Call]:
    """Steals mock calls from a responses.RequestsMock before they're destroyed at contextmanager
    exit.
    """
    return [mock_network.calls[i] for i in range(len(mock_network.calls))]


@contextmanager
def submit_listen_mock_network(context):
    with responses.RequestsMock() as mock_responses:

        # spotify gateway eagerly fetches client credentials on creation
        mock_responses.add(
            make_post_client_credentials()
        )

        if context.is_day:
            mock_responses.add(
                make_post_listen_request_day(
                    song_id=context.song_id,
                    song_provider='SPOTIFY',
                    listener_name=context.name,
                    listen_time_utc=context.current_time_utc.isoformat(),
                    note=context.note,
                    iana_timezone=context.iana_timezone
                )
            )

            mock_responses.add(make_get_track_whispers_request())

        else:
            mock_responses.add(make_post_listen_request_night())

        yield mock_responses
