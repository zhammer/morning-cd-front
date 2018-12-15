from typing import Dict, cast

import requests

from front.definitions import Listen, MusicProvider, Song, exceptions
from front.gateways.music import MusicGatewayABC


class SpotifyGateway(MusicGatewayABC):
    base_url = 'https://api.spotify.com/v1'
    auth_url = 'https://accounts.spotify.com/api/token'

    def __init__(self, client_id: str, client_secret: str) -> None:
        self.bearer_token = SpotifyGateway.fetch_bearer_token(client_id, client_secret)

    def fetch_song_of_listen(self, listen: Listen) -> Song:
        r = requests.get(
            self.base_url + '/tracks/' + listen.song_id,
            headers={'Authorization': 'Bearer ' + self.bearer_token}
        )

        if not r.status_code == requests.codes.ok:
            try:
                message = r.json()['error']['message']
            except (KeyError, ValueError):
                message = ''

            raise exceptions.MusicError(message)

        else:
            return _pluck_song(r.json())

    @staticmethod
    def fetch_bearer_token(client_id: str, client_secret: str) -> str:
        r = requests.post(
            SpotifyGateway.auth_url,
            auth=(client_id, client_secret),
            data={'grant_type': 'client_credentials'}
        )

        return cast(str, r.json()['access_token'])


def _pluck_song(raw_song: Dict) -> Song:
    return Song(
        id=raw_song['id'],
        name=raw_song['name'],
        artist_name=raw_song['artists'][0]['name'],
        album_name=raw_song['album']['name'],
        image_url_by_size={
            'large': raw_song['album']['images'][0]['url'],
            'medium': raw_song['album']['images'][1]['url'],
            'small': raw_song['album']['images'][2]['url']
        },
        music_provider=MusicProvider.SPOTIFY
    )
