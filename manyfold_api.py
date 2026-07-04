import time
import requests
import logging
from flask import current_app

logger = logging.getLogger(__name__)


class ManyfoldAPIError(Exception):
    """Manyfold API request failure. Carries the HTTP status code when available."""
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code


class ManyfoldAPI:
    """Interact with a self-hosted Manyfold instance's REST API (OAuth2 client-credentials)."""

    # In-memory access token cache keyed by (base_url, client_id) — client-credentials
    # tokens aren't tied to a particular end user, so caching per-process is safe.
    _token_cache = {}

    def __init__(self, base_url, client_id, client_secret):
        self.base_url = base_url.rstrip('/')
        self.client_id = client_id
        self.client_secret = client_secret

    def _get_token(self):
        cache_key = (self.base_url, self.client_id)
        cached = ManyfoldAPI._token_cache.get(cache_key)
        if cached and cached['expires_at'] > time.time() + 30:
            return cached['access_token']

        try:
            response = requests.post(
                f'{self.base_url}/oauth/token',
                data={
                    'grant_type': 'client_credentials',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'scope': 'read'
                },
                timeout=current_app.config.get('HTTP_TIMEOUT', 10)
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            status_code = getattr(e.response, 'status_code', None)
            body = getattr(e.response, 'text', '')
            raise ManyfoldAPIError(f"Manyfold token request failed: {str(e)} | body={body}", status_code=status_code)

        token_data = response.json()
        access_token = token_data['access_token']
        expires_in = token_data.get('expires_in', 3600)
        ManyfoldAPI._token_cache[cache_key] = {
            'access_token': access_token,
            'expires_at': time.time() + expires_in
        }
        return access_token

    def _make_request(self, method, path, **kwargs):
        token = self._get_token()
        # Without an explicit Accept header, Manyfold's content negotiation falls
        # back to its HTML web UI instead of the JSON API for these same paths.
        kwargs['headers'] = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.manyfold.v0+json, application/json'
        }
        kwargs.setdefault('timeout', current_app.config.get('HTTP_TIMEOUT', 10))

        try:
            response = requests.request(method, f'{self.base_url}{path}', **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            status_code = getattr(e.response, 'status_code', getattr(response, 'status_code', None))
            body = getattr(e.response, 'text', getattr(response, 'text', ''))[:500]
            raise ManyfoldAPIError(f"Manyfold API error: {str(e)} | status={status_code} | body={body!r}", status_code=status_code)

    def list_models(self, page=1, creator=None, collection=None, order=None):
        """Browse models. Manyfold has no free-text search — callers filter client-side."""
        params = {'page': page}
        if creator:
            params['creator'] = creator
        if collection:
            params['collection'] = collection
        if order:
            params['order'] = order
        return self._make_request('GET', '/models', params=params)

    def get_model(self, model_id):
        return self._make_request('GET', f'/models/{model_id}')

    def list_creators(self, page=1):
        return self._make_request('GET', '/creators', params={'page': page})
