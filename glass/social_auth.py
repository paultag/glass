from .models import GlassAPI

from social.apps.django_app.utils import load_strategy
from requests.exceptions import HTTPError
import requests


def request(u, *args, **kwargs):
    """
    Wrapper for request.request, but refresh the token if we can't nom.
    """
    try:
        req = requests.request(*args, **kwargs)
    except HTTPError:
        s = load_strategy(backend='google-oauth2')
        u.refresh_token(s)
        req = requests.request(*args, **kwargs)
    req.raise_for_status()
    return req.json()


class SocialGlassAPI(GlassAPI):
    def __init__(self, user):
        self._user = user

    @property
    def token(self):
        return self._user.tokens  # Token.
