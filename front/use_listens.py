from datetime import datetime
from typing import List, Optional

from front.context import Context
from front.definitions import Listen, ListenInput, Song, SortOrder


def get_listens(context: Context,
                limit: int,
                sort_order: SortOrder,
                before_utc: Optional[datetime] = None,
                after_utc: Optional[datetime] = None) -> List[Listen]:
    return context.listens_gateway.fetch_listens(
        before_utc=before_utc,
        after_utc=after_utc,
        sort_order=sort_order,
        limit=limit
    )


def get_listen(context: Context, listen_id: str) -> Listen:
    return context.listens_gateway.fetch_listen(listen_id)


def get_song_of_listen(context: Context, listen: Listen) -> Song:
    return context.music_gateway.fetch_song_of_listen(listen)


def submit_listen(context: Context, listen_input: ListenInput) -> Listen:
    return context.listens_gateway.submit_listen(listen_input)
