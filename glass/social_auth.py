from .models import GlassAPI

from social.apps.django_app.utils import load_strategy
from requests.exceptions import HTTPError
import requests


def retry(fn):
    def _fn(self, *args, **kwargs):
        try:
            return fn(self, *args, **kwargs)
        except HTTPError:
            s = load_strategy(backend='google-oauth2')
            sa = self._user.social_auth.get()
            sa.refresh_token(s)
            sa.save()
            return fn(self, *args, **kwargs)
    return _fn


class SocialGlassAPI(GlassAPI):
    def __init__(self, user):
        self._user = user

    get = retry(GlassAPI.get)
    post = retry(GlassAPI.post)

    @property
    def token(self):
        return self._user.tokens  # Token.
