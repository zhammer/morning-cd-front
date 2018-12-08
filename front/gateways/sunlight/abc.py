from abc import ABC, abstractmethod
from datetime import date

from front.definitions import SunlightWindow


class SunlightGatewayABC(ABC):

    @abstractmethod
    def fetch_sunlight_window(self, iana_timezone: str, on_date: date) -> SunlightWindow:
        ...
