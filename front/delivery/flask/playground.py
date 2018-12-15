import os
import webbrowser

from flask import Flask

from flask_graphql import GraphQLView

from front.delivery.flask.util import create_default_context, is_flask_reload
from front.delivery.graphql import schema


listens_service_api_key = os.environ['LISTENS_SERVICE_API_KEY']
sunlight_service_api_key = os.environ['SUNLIGHT_SERVICE_API_KEY']
spotify_client_id = os.environ['SPOTIFY_CLIENT_ID']
spotify_client_secret = os.environ['SPOTIFY_CLIENT_SECRET']

context = create_default_context(
    listens_service_api_key,
    sunlight_service_api_key,
    spotify_client_id,
    spotify_client_secret
)

app = Flask(__name__)
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        get_context=lambda: context,
        graphiql=True
    )
)


if is_flask_reload(os.environ):
    webbrowser.open('http://localhost:5000/graphql')
