from datetime import datetime
from typing import NamedTuple, Optional

from front.definitions import MusicProvider


class Listen(NamedTuple):
    id: str
    song_id: str
    song_provider: MusicProvider
    listener_name: str
    listen_time_utc: datetime
    iana_timezone: str

    note: Optional[str] = None
