import pytest
from heliopy.web_app import app

@pytest.fixture
def client():
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client

def test_timeseries_api(client):
    rv = client.get('/api/plot/timeseries')
    assert rv.status_code == 200
    data = rv.get_json()
    assert 'times' in data and 'flux' in data and 'labels' in data
    assert len(data['times']) == len(data['flux']) > 0
    assert 'x' in data['labels'] and 'y' in data['labels'] and 'title' in data['labels']
