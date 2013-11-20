import requests
import json


class GlassAPI(object):
    API_BASE = 'https://www.googleapis.com/mirror/v1'

    def __init__(self, token):
        self.token = token

    def _url(self, path):
        return "%s/%s" % (self.API_BASE, path)

    def get(self, path, **kwargs):
        if 'params' not in kwargs:
            kwargs['params'] = {}

        params = kwargs.pop('params')

        params['access_token'] = self._user.social_auth.get().tokens
        return self.request('GET', self._url(path), params=params, **kwargs)

    def post(self, path, **kwargs):
        if 'data' not in kwargs:
            kwargs['data'] = {}
        data = json.dumps(kwargs.pop('data'))

        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        headers = kwargs.pop('headers')

        headers['Authorization'] = "Bearer {token}".format(
            token=self._user.social_auth.get().tokens)
        headers['Content-Type'] = "application/json"

        return self.request('POST', self._url(path), data=data,
                            headers=headers, **kwargs)

    def request(self, *args, **kwargs):
        req = requests.request(*args, **kwargs)
        req.raise_for_status()
        return req.json()


class GlassTimeline(object):
    pass


class GlassTimelineItem(object):
    pass
