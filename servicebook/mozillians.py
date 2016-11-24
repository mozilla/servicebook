import requests


class Mozillians(object):
    def __init__(self, app):
        self.endpoint = app.config['mozillians']['endpoint']
        self.key = app.config['mozillians']['api_key']
        self._cache = {}
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['mozillians'] = self

    def get_info(self, email):
        if email in self._cache:
            url = self._cache[email]
        else:
            url = '?api-key=%s&email=%s&format=json'
            url = url % (self.key, email)
            user = requests.get(self.endpoint + url).json()
            if 'results' not in user:
                return {}

            res = user['results']
            if len(res) == 0:
                return {}

            url = res[0]['_url']
            self._cache[email] = url

        url = url + '?api-key=%s&format=json'
        url = url % self.key
        details = requests.get(url).json()
        return details
