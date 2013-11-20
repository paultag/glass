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


class GlassAPIObject(object):
    def to_obj(self):
        pass

    def to_json(self):
        return json.dumps(self.to_obj())


class GlassTimelineItemMenu(GlassAPIObject):
    ACTIONS = ['CUSTOM',  # Trigger callback to API
        'REPLY', 'REPLY_ALL', 'DELETE', 'SHARE', 'READ_ALOUD',
        'VOICE_CALL', 'NAVIGATE', 'TOGGLE_PINNED',
        'OPEN_URI',  # Needs `payload'
        'PLAY_VIDEO',  # Needs `payload'
    ]

    def __init__(self, id_, action, payload=None):
        if action not in self.ACTIONS:
            raise ValueError("Action `%s' is invalid" % (action))

        if action in ['OPEN_URI', 'PLAY_VIDEO'] and payload is None:
            raise ValueError("Action requires a payload kwarg.")

        self.action = action
        self.id_ = id_
        self.payload = payload


    def to_obj(self):
        o = {
            "id": self.id_,
            "action": self.action,
        }
        if self.payload:
            o['payload'] = self.payload
        return o


class GlassTimelineItem(GlassAPIObject):
    pass
