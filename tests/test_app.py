from project import app
from flask_testing import TestCase

class MyTest(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_index(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/login')
