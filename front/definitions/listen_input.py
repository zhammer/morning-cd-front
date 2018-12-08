from typing import NamedTuple

from front.definitions import MusicProvider


class ListenInput(NamedTuple):
    song_id: str
    song_provider: MusicProvider
    listener_name: str
    note: str
    iana_timezone: str
