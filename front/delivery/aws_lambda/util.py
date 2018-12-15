from front.context import Context
from front.gateways.listens import ListensServiceGateway
from front.gateways.music import SpotifyGateway
from front.gateways.sunlight import SunlightServiceGateway


def create_default_context(listens_service_api_key: str,
                           sunlight_service_api_key: str,
                           spotify_client_id: str,
                           spotify_client_secret: str) -> Context:
    return Context(
        listens_gateway=ListensServiceGateway(listens_service_api_key),
        sunlight_gateway=SunlightServiceGateway(sunlight_service_api_key),
        music_gateway=SpotifyGateway(spotify_client_id, spotify_client_secret)
    )
