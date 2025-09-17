from django.urls import reverse


def test_health_check_success(db, client):
    """
    Test the health check endpoint.
    """
    response = client.get(reverse('health_check'))
    data = response.json()['data']

    assert response.status_code == 200

    assert data['status'] == 'ok'
    assert 'timestamp' in data
    assert 'version' in data
    assert 'uptime_seconds' in data
    assert 'database' in data
    assert data['database']['status'] == 'ok'
    assert 'environment' in data
    assert 'metrics' in data
    assert 'python_version' in data['metrics']
    assert 'debug_mode' in data['metrics']


def test_health_check_db_error(client, monkeypatch):
    def mock_db_check():
        return {'status': 'error', 'message': 'Database error'}

    monkeypatch.setattr('simple_blog.health.check_database', mock_db_check)

    response = client.get(reverse('health_check'))
    data = response.json()['data']

    assert response.status_code == 503
    assert data['status'] == 'error'
    assert data['database']['status'] == 'error'
    assert data['database']['message'] == 'Database error'
