from abc import ABC, abstractmethod

from front.definitions import Listen, Song


class MusicGatewayABC(ABC):

    @abstractmethod
    def fetch_song_of_listen(self, listen: Listen) -> Song:
        ...
