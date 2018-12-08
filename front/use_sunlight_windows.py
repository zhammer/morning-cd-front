from datetime import date

from front.context import Context
from front.definitions import SunlightWindow


def get_sunlight_window(context: Context, iana_timezone: str, on_date: date) -> SunlightWindow:
    return context.sunlight_gateway.fetch_sunlight_window(
        iana_timezone,
        on_date
    )
