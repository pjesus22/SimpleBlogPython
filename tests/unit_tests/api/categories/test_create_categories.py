import json

from django.urls import reverse

from apps.content.models import Category


def mock_data():
    return {
        'name': 'test category',
        'description': 'fake category description',
    }


def post_category(client, payload, as_json=True):
    data = json.dumps(payload) if as_json else payload
    return client.post(
        path=reverse('category-list'),
        data=data,
        content_type='application/json',
    )


def build_expected_error(
    response_data, detail, status=400, title='Bad Request', index=0
):
    return {
        'status': str(status),
        'title': title,
        'detail': detail,
        'meta': response_data['errors'][index]['meta'],
    }


def test_post_category_201_created(db, logged_admin_client):
    payload = mock_data()
    response = post_category(logged_admin_client, payload)
    assert response.status_code == 201


def test_post_category_invalid_fields(db, logged_admin_client):
    payload = mock_data()
    payload.update({'invalid': 'Invalid Field'})

    response = post_category(logged_admin_client, payload)
    response_data = response.json()

    expected = build_expected_error(response_data, detail='This field is not allowed.')

    assert response.status_code == 400
    assert expected in response_data.get('errors')


def test_post_category_json_decode_error(db, logged_admin_client):
    payload = "'{invalid json"

    response = post_category(logged_admin_client, payload, as_json=False)
    response_data = response.json()

    expected = build_expected_error(
        response_data, detail='Invalid JSON: Expecting value: line 1 column 1 (char 0)'
    )

    assert response.status_code == 400
    assert expected in response_data.get('errors')


def test_post_category_validation_error(db, logged_admin_client):
    payload = {'name': 'fake name' * 10, 'description': 'fake category description'}

    response = post_category(logged_admin_client, payload)
    response_data = response.json()

    expected = [
        build_expected_error(
            response_data,
            detail='Ensure this value has at most 50 characters (it has 90).',
            index=0,
        ),
        build_expected_error(
            response_data,
            detail='Ensure this value has at most 50 characters (it has 90).',
            index=1,
        ),
    ]

    assert response.status_code == 400
    assert expected == response_data['errors']


def test_post_category_generic_exception(db, logged_admin_client, override):
    def fake_save(*args, **kwargs):
        raise Exception('Something went wrong')

    payload = mock_data()

    with override(Category, 'save', fake_save):
        response = post_category(logged_admin_client, payload)

    response_data = response.json()

    expected = build_expected_error(
        status='500',
        title='Internal Server Error',
        detail='Something went wrong',
        response_data=response_data,
    )

    assert response.status_code == 500
    assert expected in response_data['errors']
