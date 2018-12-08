from typing import Dict, NamedTuple

from front.definitions import MusicProvider


class Song(NamedTuple):
    id: str
    music_provider: MusicProvider
    name: str
    artist_name: str
    album_name: str
    image_url_by_size: Dict[str, str]
