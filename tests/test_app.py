import pytest
import sys
sys.path.append('..') 
from project import app as flask_app

@pytest.fixture
def app():
    app = flask_app
    app.config.update({"TESTING": True, "SECRET_KEY": "01234566"})
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def login(client, email, password):
    return client.post('/login', data=dict(email=email, password=password), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

# Patient Tests
def test_patient_login(client):
    response = login(client, 'ak@gmail.com', 'ak1234')
    assert 'Patient Dashboard' in response.get_data(as_text=True)

def test_patient_view_measurements(client):
    login(client, 'ak@gmail.com', 'ak1234')
    response = client.get('/view_measurements', follow_redirects=True)
    assert 'Your Measurements' in response.get_data(as_text=True)

def test_patient_book_appointment(client):
    login(client, 'ak@gmail.com', 'ak1234')
    response = client.get('/book_appointment', follow_redirects=True)
    assert 'Book an Appointment' in response.get_data(as_text=True)

# Medical Professional Tests
def test_mp_login(client):
    response = login(client, 'mp@gmail.com', 'mp1234')
    assert 'Medical Professional Dashboard' in response.get_data(as_text=True)

def test_mp_browse_patients(client):
    login(client, 'mp@gmail.com', 'mp1234')
    response = client.get('/browse_patients', follow_redirects=True)
    assert 'Patients List' in response.get_data(as_text=True)

def test_mp_manage_appointments(client):
    login(client, 'mp@gmail.com', 'mp1234')
    response = client.get('/manage_appointments', follow_redirects=True)
    assert 'Manage Appointments' in response.get_data(as_text=True)

# Admin Tests
def test_admin_login(client):
    response = login(client, 'admin@gmail.com', 'admin')
    assert 'Admin Dashboard' in response.get_data(as_text=True)

def test_admin_assign_roles(client):
    login(client, 'admin@gmail.com', 'admin')
    response = client.get('/manage_roles', follow_redirects=True)
    assert 'Manage Roles' in response.get_data(as_text=True)
    