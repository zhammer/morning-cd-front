from responses import Response


def make_get_sunlight_window_response(iana_timezone: str,
                                      date: str,
                                      sunrise_utc: str,
                                      sunset_utc: str) -> Response:
    return Response(
        method='GET',
        url=f'https://api.morningcd.com/sunlight?iana_timezone={iana_timezone}&on_date={date}',
        json={
            'sunrise_utc': sunrise_utc,
            'sunset_utc': sunset_utc
        }
    )
