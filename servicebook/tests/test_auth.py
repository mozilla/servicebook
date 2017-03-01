import base64
from servicebook.tests.support import BaseTest
from servicebook.mappings import AuthenticationKey
from servicebook.db import Session


def _key2header(key):
    key = base64.b64encode(key.encode('ascii'))
    return 'APIKey ' + key.decode('ascii')


class AuthTest(BaseTest):
    def setUp(self):
        super(AuthTest, self).setUp()
        session = Session()
        reader = AuthenticationKey('reader', scope='read')
        writer = AuthenticationKey('reader', scope='readwrite')
        admin = AuthenticationKey('reader', scope='admin')
        session.add(reader)
        session.add(writer)
        session.add(admin)
        session.commit()

        self.reader_headers = {'Authorization': _key2header(reader.key)}
        self.writer_headers = {'Authorization': _key2header(writer.key)}
        self.admin_headers = {'Authorization': _key2header(admin.key)}

        # let's protect the app
        self.config = self.app.app.config
        self.config['common']['anonymous_access'] = 'peanuts'

    def tearDown(self):
        self.config['common']['anonymous_access'] = 'readwrite'
        super(AuthTest, self).tearDown()

    def _post_project(self, headers=None, status=201):
        if headers is None:
            headers = {}
        else:
            headers = dict(headers)
        attrs = {'name': 'new proj'}
        headers['Content-Type'] = 'application/vnd.api+json'
        req_data = {'data': {'type': 'project', 'attributes': attrs}}
        self.app.post_json('/api/project', params=req_data,
                           headers=headers, status=status)

    def test_anonymous(self):
        # everyting should 401
        self.app.get('/api', status=401)
        self.app.post('/api', status=401)

        # now let's open READS
        self.config['common']['anonymous_access'] = 'read'
        self.app.get('/api', status=200)
        self.app.post('/api', status=401)

        # and writes
        self.config['common']['anonymous_access'] = 'readwrite'
        self.app.get('/api', status=200)
        self._post_project()

    def test_reader(self):
        # a reader should be able to read data
        self.app.get('/api', status=200, headers=self.reader_headers)
        # but not to post
        self.app.post('/api', status=401, headers=self.reader_headers)

    def test_writer(self):
        # a writer should be able to read data
        self.app.get('/api', status=200, headers=self.writer_headers)
        # and also post
        self._post_project(headers=self.writer_headers)

    def test_admin(self):
        # an admin should be able to read data
        self.app.get('/api', status=200, headers=self.admin_headers)
        # and also post
        self._post_project(headers=self.admin_headers)

    def test_bad_auth(self):
        funky_headers = {'Authorization': 'prout'}
        self._post_project(headers=funky_headers, status=401)

        funky_headers = {'Authorization': 'Basic meh'}
        self._post_project(headers=funky_headers, status=401)

        funky_headers = {'Authorization': 'ApiKey wat'}
        self._post_project(headers=funky_headers, status=401)

        unknown = _key2header('unknown')
        funky_headers = {'Authorization': 'ApiKey ' + unknown}
        self._post_project(headers=funky_headers, status=401)
