from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from front.definitions import Listen, ListenInput, SortOrder


class ListensGatewayABC(ABC):

    @abstractmethod
    def fetch_listen(self, listen_id: str) -> Listen:
        ...

    @abstractmethod
    def fetch_listens(self,
                      limit: int,
                      sort_order: SortOrder,
                      before_utc: Optional[datetime],
                      after_utc: Optional[datetime]) -> List[Listen]:
        ...

    @abstractmethod
    def submit_listen(self, listen_input: ListenInput) -> Listen:
        ...
