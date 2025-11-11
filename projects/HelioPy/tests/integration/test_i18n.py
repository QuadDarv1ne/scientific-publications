import re
import pytest

from heliopy.web_app import app

@pytest.fixture
def client():
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client

def test_home_lang_switch_en(client):
    rv = client.get('/?lang=en')
    assert rv.status_code == 200
    html = rv.get_data(as_text=True)
    assert 'Welcome to HelioPy web interface!' in html
    assert re.search(r'<html[^>]*lang="en"', html)

def test_home_lang_switch_ru(client):
    rv = client.get('/?lang=ru')
    assert rv.status_code == 200
    html = rv.get_data(as_text=True)
    assert 'Добро пожаловать' in html
    assert re.search(r'<html[^>]*lang="ru"', html)

def test_analysis_lang_en(client):
    client.get('/?lang=en')
    rv = client.get('/analysis')
    assert rv.status_code == 200
    html = rv.get_data(as_text=True)
    assert 'Peak flux' in html


def test_analysis_lang_ru(client):
    client.get('/?lang=ru')
    rv = client.get('/analysis')
    assert rv.status_code == 200
    html = rv.get_data(as_text=True)
    assert 'Пиковый поток' in html
