from flask_testing import TestCase
from project import app, db  # Import your Flask app and database

class MyTest(TestCase):

    def create_app(self):
        # Configure your app for testing
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        return app

    def setUp(self):
        # Setup your app context and database for each test
        db.create_all()

    def tearDown(self):
        # Tear down and clean up after each test
        db.session.remove()
        db.drop_all()

    def test_index_route(self):
        # Test your route
        response = self.client.get('/')
        self.assert200(response)  # Assert the response status code is 200
        self.assertIn('Welcome', response.data.decode())  # Optionally, check if certain content is in the response
