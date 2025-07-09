import pytest
from django.urls import reverse


def mock_data(**kwargs):
    base = {'name': 'test category', 'description': 'fake category description'}
    if kwargs:
        base.update(kwargs)
        return base
    return base


def post_category(client, payload):
    data = payload
    return client.post(
        path=reverse('category-list'), data=data, content_type='application/json'
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


@pytest.mark.parametrize(
    'payload, detailed_error',
    [
        (mock_data(invalid='Invalid Field'), 'This field is not allowed.'),
        ("'{invalid json", 'Invalid JSON: Expecting value: line 1 column 1 (char 0)'),
        (
            {'name': 'x' * 51},
            'Ensure this value has at most 50 characters (it has 51).',
        ),
        ({'name': ''}, 'This field cannot be blank.'),
    ],
)
def test_post_category_validation_errors(
    db, logged_admin_client, payload, detailed_error
):
    response = post_category(logged_admin_client, payload)
    response_data = response.json()

    expected = build_expected_error(response_data, detail=detailed_error)

    assert response.status_code == 400
    assert expected in response_data.get('errors')


def test_post_category_generic_exception(db, monkeypatch, logged_admin_client):
    payload = mock_data()

    def fake_save(*args, **kwargs):
        raise Exception('Something went wrong')

    monkeypatch.setattr('apps.content.views.categories.Category.save', fake_save)

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
