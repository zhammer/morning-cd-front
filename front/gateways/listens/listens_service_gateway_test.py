import os
from datetime import datetime

from faaspact_maker import (
    Interaction,
    PactMaker,
    ProviderState,
    RequestWithMatchers,
    ResponseWithMatchers,
    matchers
)

import pytest

from front.definitions import Listen, MusicProvider, exceptions
from front.gateways.listens import ListensServiceGateway


PACT_DIRECTORY = os.environ.get('PACT_DIRECTORY', 'pacts')


class TestFetchListen:

    def test_fetches_listen_by_id(self) -> None:
        # Given a listens service gateway
        listens_service_gateway = ListensServiceGateway(api_key='xyz')

        # And this pact with the listens service
        listen_fields = {
            'id': '1',
            'song_id': '58yFroDNbzHpYzvicaC0de',
            'song_provider': 'SPOTIFY',
            'listener_name': 'Andre 3',
            'listen_time_utc': '2018-12-07T21:35:46',
            'iana_timezone': 'America/New_York',
            'note': 'I like this song!'
        }
        pact = PactMaker(
            'front', 'listens', 'https://micro.morningcd.com',
            pact_directory=PACT_DIRECTORY
        )
        pact.add_interaction(Interaction(
            description='a request for a listen',
            provider_states=(ProviderState(
                name='a listen exists with the fields',
                params={'fields': listen_fields}),
            ),
            request=RequestWithMatchers(
                method='GET',
                path='/listens/1',
            ),
            response=ResponseWithMatchers(
                status=200,
                body=listen_fields
            )
        ))

        # When we request a listen from the listens service
        with pact.start_mocking():
            listen = listens_service_gateway.fetch_listen('1')

        # Then we get the listen from the listens service
        expected_listen = Listen(
            id='1',
            song_id='58yFroDNbzHpYzvicaC0de',
            song_provider=MusicProvider.SPOTIFY,
            listener_name='Andre 3',
            listen_time_utc=datetime(2018, 12, 7, 21, 35, 46),
            iana_timezone='America/New_York',
            note='I like this song!'
        )
        assert listen == expected_listen

    def test_raises_listens_error_if_listen_doesnt_exist(self) -> None:
        # Given a listens service gateway
        listens_service_gateway = ListensServiceGateway(api_key='xyz')

        # And this pact with the listens service
        pact = PactMaker(
            'front', 'listens', 'https://micro.morningcd.com',
            pact_directory=PACT_DIRECTORY
        )
        pact.add_interaction(Interaction(
            description='a request for a listen',
            provider_states=(ProviderState(
                name='there are no listens in the database'
            ),),
            request=RequestWithMatchers(
                method='GET',
                path='/listens/1'
            ),
            response=ResponseWithMatchers(
                status=404,
                body={'message': matchers.Like('No listen exists with id 1')}
            )
        ))

        # When we request a listen from the listens service
        with pact.start_mocking():
            with pytest.raises(exceptions.ListensError):
                listens_service_gateway.fetch_listen('1')
