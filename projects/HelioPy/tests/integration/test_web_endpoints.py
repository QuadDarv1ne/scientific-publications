import json
import pytest

from heliopy.web_app import app

@pytest.fixture
def client():
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client

def test_ping(client):
    rv = client.get('/ping')
    assert rv.status_code == 200
    assert rv.get_json()['status'] == 'ok'

def test_api_info(client):
    rv = client.get('/api/info')
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'name' in data and data['name'] == 'HelioPy'


def test_flare_classify(client):
    rv = client.get('/api/flare/classify?flux=1e-6')
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'class' in data


def test_time_carrington(client):
    rv = client.get('/api/time/carrington?time=2023-10-15 12:00:00')
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'carrington_rotation' in data


def test_coords_convert(client):
    rv = client.post('/api/coords/convert', json={"r":1.0, "theta":0.5, "phi":0.2})
    assert rv.status_code == 200
    data = rv.get_json()
    assert set(data.keys()) == {"x","y","z"}
