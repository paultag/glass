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

    def delete(self, path, **kwargs):
        return self.pud('DELETE', path, **kwargs)

    def post(self, path, **kwargs):
        return self.pud('POST', path, **kwargs)

    def pud(self, method, path, **kwargs):

        data = None
        if 'data' in kwargs:
            data = json.dumps(kwargs.pop('data'), cls=JSONEncoderPlus)

        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        headers = kwargs.pop('headers')

        headers['Authorization'] = "Bearer {token}".format(
            token=self._user.social_auth.get().tokens)

        if data:
            headers['Content-Type'] = "application/json"

        return self.request(method, self._url(path), data=data,
                            headers=headers, **kwargs)

    def request(self, *args, **kwargs):
        req = requests.request(*args, **kwargs)
        req.raise_for_status()
        if req.text:
            return req.json()
        return None

    def get_timeline(self):
        return GlassTimeline(self)

    def get_location(self):
        return GlassLocationService(self)


class GlassLocationService(object):
    def __init__(self, api):
        self.api = api

    def get_current_location(self):
        data = self.api.get('locations/latest')
        return GlassLocation(data)


class GlassLocation(object):
    def __init__(self, obj):
        self.kind = obj['kind']
        self.when = obj['timestamp']
        self.lon = obj['longitude']
        self.lat = obj['latitude']
        self.accuracy = obj['accuracy']
        self.id = obj['id']


class GlassTimeline(object):
    def __init__(self, api):
        self.api = api

    def add_item(self, item):
        data = self.api.post('timeline', data=item.to_obj())
        id = data['id']
        item.id = id
        return id

    def delete_item(self, id):
        self.api.delete('timeline/%s' % (id))
        return None

    def get_page(self, page=None):
        params = {}
        if page:
            params['pageToken'] = page
        return self.api.get('timeline', params=params)

    def __iter__(self):
        curpage = self.get_page()
        while curpage['items'] != []:
            for x in curpage['items']:
                yield GlassTimelineItem(**x)
            curpage = self.get_page(page=curpage['nextPageToken'])


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
        'id': 'id',
        'payload': 'payload',
    }

    def __init__(self, id, action, payload=None):
        if action not in self.ACTIONS:
            raise ValueError("Action `%s' is invalid" % (action))

        if action in ['OPEN_URI', 'PLAY_VIDEO'] and payload is None:
            raise ValueError("Action requires a payload kwarg.")

        self.action = action
        self.id = id
        self.payload = payload


class GlassTimelineItem(GlassAPIObject):
    _attrs = {
        # host: remote
        'menu_items': 'menuItems',
        'text': 'text',
        'html': 'html',
        'notification': 'notification',
    }

    KINDS = ['mirror#timelineItem',]

    def __init__(self, id=None, kind=None, menuItems=None, updated=None,
                 created=None, text=None, html=None, notification=None,
                 creator=None, etag=None, selfLink=None):

        if kind and kind not in self.KINDS:
            raise ValueError("Kind `%s' is invalid" % (kind))

        self.menu_items = []
        if menuItems:
            self.menu_items = [GlassTimelineItemMenu(**x) for x in menuItems]

        self.text = None
        self.html = None
        self.notification = None
        self.kind = kind
        self.created = created
        self.updated = updated
        self.etag = etag
        self.id = id
        self.self_link = selfLink
        self.notification = notification
        self.creator = creator

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
        self.add_menu_item(GlassTimelineItemMenu(id=str(uuid.uuid4()),
                                                 action='DELETE'))

class BoringGlassTimelineItem(
    NotifiableGlassTimelineItem, DeletableGlassTimelineItem
):
    pass
