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

from front.definitions import Listen, MusicProvider, SortOrder, exceptions
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


class TestFetchListens:

    def test_fetches_listen_in_range(self) -> None:
        # Given a listens service gateway
        listens_service_gateway = ListensServiceGateway(api_key='xyz')

        # And this pact with the listens service
        pact = PactMaker(
            'front', 'listens', 'https://micro.morningcd.com',
            pact_directory=PACT_DIRECTORY
        )
        pact.add_interaction(Interaction(
            description='a request for listens',
            provider_states=(
                ProviderState(
                    name='a listen exists with the fields',
                    params={
                        'fields': {
                            'listener_name': 'Alex',
                            'listen_time_utc': '2018-12-06T10:30:00',
                        }
                    }
                ),
                ProviderState(
                    name='a listen exists with the fields',
                    params={
                        'fields': {
                            'listener_name': 'Barack',
                            'listen_time_utc': '2018-12-06T11:30:00',
                        }
                    }
                ),
                ProviderState(
                    name='a listen exists with the fields',
                    params={
                        'fields': {
                            'listener_name': 'Dorothy',
                            'listen_time_utc': '2018-12-06T12:30:00',
                        }
                    }
                ),
                ProviderState(
                    name='a listen exists with the fields',
                    params={
                        'fields': {
                            'listener_name': 'Farrah',
                            'listen_time_utc': '2018-12-06T13:30:00',
                        }
                    }
                ),
                ProviderState(
                    name='a listen exists with the fields',
                    params={
                        'fields': {
                            'listener_name': 'Farrah',
                            'listen_time_utc': '2018-12-06T14:30:00',
                        }
                    }
                )
            ),
            request=RequestWithMatchers(
                method='GET',
                path='/listens',
                query={
                    'after_utc': ['2018-12-06T12:00:00'],
                    'before_utc': ['2018-12-06T14:00:00'],
                    'sort_order': ['descending'],
                    'limit': ['10']
                }
            ),
            response=ResponseWithMatchers(
                status=200,
                body={'items': [
                    {
                        'id': matchers.Like('4'),
                        'song_id': matchers.Like('a song id'),
                        'song_provider': matchers.Like('SPOTIFY'),
                        'listener_name': 'Farrah',
                        'listen_time_utc': '2018-12-06T13:30:00',
                        'iana_timezone': matchers.Like('America/New_York'),
                        'note': matchers.Like('I like this song!')
                    },
                    {
                        'id': matchers.Like('3'),
                        'song_id': matchers.Like('a song id'),
                        'song_provider': matchers.Like('SPOTIFY'),
                        'listener_name': 'Dorothy',
                        'listen_time_utc': '2018-12-06T12:30:00',
                        'iana_timezone': matchers.Like('America/New_York'),
                        'note': matchers.Like('I like this song!')
                    }
                ]}
            )
        ))

        # When we request listens in a range
        with pact.start_mocking():
            listens = listens_service_gateway.fetch_listens(
                limit=10,
                sort_order=SortOrder.DESCENDING,
                after_utc=datetime(2018, 12, 6, 12, 0, 0),
                before_utc=datetime(2018, 12, 6, 14, 0, 0)
            )

        # Then we get the two listens in that time range
        assert len(listens) == 2
        assert listens[0].listener_name == 'Farrah'
        assert listens[0].listen_time_utc == datetime(2018, 12, 6, 13, 30, 0)
        assert listens[1].listener_name == 'Dorothy'
        assert listens[1].listen_time_utc == datetime(2018, 12, 6, 12, 30, 0)

    def test_fetches_empty_list_if_no_listens(self) -> None:

        # Given a listens service gateway
        listens_service_gateway = ListensServiceGateway(api_key='xyz')

        # And this pact with the listens service
        pact = PactMaker(
            'front', 'listens', 'https://micro.morningcd.com',
            pact_directory=PACT_DIRECTORY
        )
        pact.add_interaction(Interaction(
            description='a request for listens',
            provider_states=(ProviderState('there are no listens in the database'),),
            request=RequestWithMatchers(
                method='GET',
                path='/listens',
                query={
                    'limit': ['10'],
                    'sort_order': ['ascending']
                }
            ),
            response=ResponseWithMatchers(
                status=200,
                body={'items': []}
            )
        ))

        # When we request listens from the listens service
        with pact.start_mocking():
            listens = listens_service_gateway.fetch_listens(10, SortOrder.ASCENDING)

        # Then we get an empty list
        assert listens == []
