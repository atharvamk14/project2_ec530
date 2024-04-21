import os
import pytest
from flask_testing import TestCase
from unittest.mock import patch
from project import app  # Import your Flask app here

class TestRoutes(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_index_redirect(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/login')

    def test_login_page(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)

    # Add more tests for other routes

class TestFormSubmission(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        return app

    @patch('your_flask_app.pyodbc.connect')
    def test_add_user(self, mock_connect):
        mock_cursor = mock_connect.return_value.cursor.return_value
        mock_cursor.fetchone.return_value = None  # Assume user does not exist
        response = self.client.post('/add_user', data={
            'name': 'Test User',
            'email': 'test@user.com',
            'password': 'password123',
            'role': '1'
        })
        self.assertRedirects(response, '/add_user')
        mock_cursor.execute.assert_called()  # Check if INSERT query was executed

    # Add more tests for other forms


@patch('your_flask_app.pyodbc.connect')
def test_user_login(mock_connect):
    mock_cursor = mock_connect.return_value.cursor.return_value
    mock_cursor.fetchone.return_value = [1, 'Test User', 'Patient']  # Mocked DB response
    with app.test_client() as client:
        response = client.post('/login', data={
            'email': 'test@user.com',
            'password': 'password123'
        })
        # Verify redirect based on user role
        self.assertRedirects(response, '/patient_home')


