from apps.utils.jsonapi_responses import JsonApiResponseBuilder


def test_build_response_with_links():
    data = {'id': '1', 'name': 'test'}
    test_links = {'self': '/api/v1/test/1', 'related': '/api/v1/related'}

    response = JsonApiResponseBuilder._build_response(data=data, links=test_links)

    assert 'links' in response
    assert response['links'] == test_links
    assert response['data'] == data
    assert 'errors' not in response
