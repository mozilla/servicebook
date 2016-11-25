from webtest.app import AppError
from servicebook.tests.support import BaseTest


class EditTest(BaseTest):
    def test_edit_project(self):

        # first attempt fails since we're not logged in
        self.assertRaises(AppError, self.app.get, '/projects/1/edit')

        # now logging in
        with self.logged_in():
            project = self.app.get('/projects/1/edit')
            form = project.forms[0]
            old_name = form['name'].value
            form['name'] = 'new name'
            form.submit()

            # let's check it changed
            self.assertTrue(b'new name' in self.app.get('/projects/1').body)

            # change it back to the old value
            project = self.app.get('/projects/1/edit')
            form = project.forms[0]
            form['name'] = old_name
            form.submit()
