from datetime import datetime
from typing import Dict, List, Optional

import requests

from front.definitions import Listen, ListenInput, MusicProvider, SortOrder
from front.definitions.exceptions import ListensError
from front.gateways.listens import ListensGatewayABC


class ListensServiceGateway(ListensGatewayABC):
    endpoint = 'https://micro.morningcd.com/listens'

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def fetch_listen(self, listen_id: str) -> Listen:
        r = requests.get(f'{self.endpoint}/{listen_id}', headers={'x-api-key': self.api_key})

        if not r.status_code == requests.codes.ok:
            message = r.json().get('message', '')
            raise ListensError(message)

        return _pluck_listen(r.json())

    def fetch_listens(self,
                      limit: int,
                      sort_order: SortOrder,
                      before_utc: Optional[datetime] = None,
                      after_utc: Optional[datetime] = None) -> List[Listen]:
        params = _build_fetch_listens_params(limit, sort_order, before_utc, after_utc)
        r = requests.get(self.endpoint, params=params, headers={'x-api-key': self.api_key})

        if not r.status_code == requests.codes.ok:
            message = r.json().get('message', '')
            raise ListensError(message)

        return _pluck_listens(r.json()['items'])

    def submit_listen(self, listen_input: ListenInput) -> Listen:
        body = _build_submit_listen_body(listen_input)
        r = requests.post(self.endpoint, json=body, headers={'x-api-key': self.api_key})

        if not r.status_code == requests.codes.ok:
            message = r.json().get('message', '')
            raise ListensError(message)

        return _pluck_listen(r.json())


def _build_submit_listen_body(listen_input: ListenInput) -> Dict:
    return {
        'song_id': listen_input.song_id,
        'song_provider': listen_input.song_provider.name,
        'listener_name': listen_input.listener_name,
        'note': listen_input.note,
        'iana_timezone': listen_input.iana_timezone
    }


def _build_fetch_listens_params(limit: int,
                                sort_order: SortOrder,
                                before_utc: Optional[datetime] = None,
                                after_utc: Optional[datetime] = None) -> Dict:
    params = {
        'limit': limit,
        'sort_order': _build_sort_order(sort_order)
    }

    if before_utc:
        params['before_utc'] = before_utc.isoformat()

    if after_utc:
        params['after_utc'] = after_utc.isoformat()

    return params


def _build_sort_order(sort_order: SortOrder) -> str:
    if sort_order == SortOrder.ASCENDING:
        return 'ascending'

    else:
        return 'descending'


def _pluck_listen(raw_listen: Dict) -> Listen:
    return Listen(
        id=raw_listen['id'],
        song_id=raw_listen['song_id'],
        song_provider=MusicProvider[raw_listen['song_provider']],
        listener_name=raw_listen['listener_name'],
        listen_time_utc=_pluck_datetime(raw_listen['listen_time_utc']),
        iana_timezone=raw_listen['iana_timezone'],
        note=raw_listen['note']
    )


def _pluck_listens(raw_listens: List[Dict]) -> List[Listen]:
    return [_pluck_listen(raw_listen) for raw_listen in raw_listens]


def _pluck_datetime(raw_datetime: str) -> datetime:
    return datetime.fromisoformat(raw_datetime).replace(tzinfo=None)
