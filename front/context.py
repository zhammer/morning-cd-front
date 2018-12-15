from typing import NamedTuple

from front.gateways.listens import ListensGatewayABC
from front.gateways.music import MusicGatewayABC
from front.gateways.sunlight import SunlightGatewayABC


class Context(NamedTuple):
    listens_gateway: ListensGatewayABC
    music_gateway: MusicGatewayABC
    sunlight_gateway: SunlightGatewayABC
