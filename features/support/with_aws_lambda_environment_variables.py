import os
from typing import Generator
from unittest.mock import patch

import behave


@behave.fixture  # type: ignore
def with_aws_lambda_environment_variables(context: behave.runner.Context) -> Generator:
    mock_env = {
        'SPOTIFY_CLIENT_ID': 'mock spotify client id',
        'SPOTIFY_CLIENT_SECRET': 'mock spotify_client_secret',
        'LISTENS_SERVICE_API_KEY': 'mock listens service api key',
        'SUNLIGHT_SERVICE_API_KEY': 'mock sunlight service api key'
    }

    with patch.dict(os.environ, mock_env):
        yield
