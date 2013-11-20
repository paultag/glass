import datetime as dt
import requests
import json
import time
import uuid


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
        data = json.dumps(kwargs.pop('data'), cls=JSONEncoderPlus)

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


class JSONEncoderPlus(json.JSONEncoder):
    def default(self, obj, **kwargs):
        if isinstance(obj, GlassAPIObject):
            return obj.to_obj()
        if isinstance(obj, dt.datetime):
            return time.mktime(obj.utctimetuple())
        #elif isinstance(obj, dt.date):
        #    return time.mktime(obj.timetuple())
        return super(JSONEncoderPlus, self).default(obj, **kwargs)


class GlassAPIObject(object):
    _attrs = {}

    def to_obj(self):
        obj = {}
        for k, v in self._attrs.items():
            a = getattr(self, k)
            if a:
                obj[v] = a
        return obj

    def to_json(self):
        return json.dumps(self.to_obj(), cls=JSONEncoderPlus)


class GlassTimelineItemMenu(GlassAPIObject):
    ACTIONS = ['CUSTOM',  # Trigger callback to API
        'REPLY', 'REPLY_ALL', 'DELETE', 'SHARE', 'READ_ALOUD',
        'VOICE_CALL', 'NAVIGATE', 'TOGGLE_PINNED',
        'OPEN_URI',  # Needs `payload'
        'PLAY_VIDEO',  # Needs `payload'
    ]

    _attrs = {
        'action': 'action',
        'id_': 'id',
        'payload': 'payload',
    }

    def __init__(self, id_, action, payload=None):
        if action not in self.ACTIONS:
            raise ValueError("Action `%s' is invalid" % (action))

        if action in ['OPEN_URI', 'PLAY_VIDEO'] and payload is None:
            raise ValueError("Action requires a payload kwarg.")

        self.action = action
        self.id_ = id_
        self.payload = payload


class GlassTimelineItem(GlassAPIObject):
    _attrs = {
        # host: remote
        'menu_items': 'menuItems',
        'text': 'text',
        'html': 'html',
        'notification': 'notification',
    }

    def __init__(self, menu_items=None, text=None, html=None):
        self.menu_items = []
        if menu_items:
            self.menu_items = menu_items

        self.text = None
        self.html = None
        self.notification = None

        if text and html:
            raise ValueError("You gave me both Text and HTML. Fail.")

        if text is None and html is None:
            raise ValueError("You gave me neither HTML nor Text")

        if text:
            self.text = text

        if html:
            self.html = html

    def add_menu_item(self, option):
        self.menu_items.append(option)


class NotifiableGlassTimelineItem(GlassTimelineItem):
    def __init__(self, *args, **kwargs):
        super(NotifiableGlassTimelineItem, self).__init__(*args, **kwargs)
        self.notification = {
            "level": "DEFAULT",  # Only one.
        }

class DeletableGlassTimelineItem(GlassTimelineItem):
    def __init__(self, *args, **kwargs):
        super(DeletableGlassTimelineItem, self).__init__(*args, **kwargs)
        self.add_menu_item(GlassTimelineItemMenu(id_=str(uuid.uuid4()),
                                                 action='DELETE'))

class BoringGlassTimelineItem(
    NotifiableGlassTimelineItem, DeletableGlassTimelineItem
):
    pass
