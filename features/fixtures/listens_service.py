from responses import Response


def make_post_listen_request_day(song_id: str,
                                 song_provider: str,
                                 listener_name: str,
                                 listen_time_utc: str,
                                 note: str,
                                 iana_timezone: str) -> Response:

    return Response(
        method='POST',
        url='https://micro.morningcd.com/listens',
        json={
            'id': '1',
            'song_id': song_id,
            'song_provider': song_provider,
            'listener_name': listener_name,
            'listen_time_utc': listen_time_utc,
            'iana_timezone': iana_timezone,
            'note': note
        }
    )


def make_post_listen_request_night() -> Response:
    return Response(
        method='POST',
        url='https://micro.morningcd.com/listens',
        json={
            'message': 'Listens can only be submitted during the day'
        },
        status=428
    )
