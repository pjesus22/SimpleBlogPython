import pytest
from django.urls import reverse


def build_expected_error(detail, status=400, title='Bad Request'):
    return {
        'status': str(status),
        'title': title,
        'detail': detail,
    }


def update_post(client, payload):
    return client.patch(
        path=reverse('category-detail', kwargs={'slug': 'test-category'}),
        data=payload,
        content_type='application/json',
    )


def test_patch_category_success(db, logged_admin_client, category_factory):
    category_factory.create(name='Test Category')
    payload = {'description': 'updated description'}

    response = update_post(logged_admin_client, payload)
    response_data = response.json()

    assert response.status_code == 200
    assert response_data['data']['attributes']['description'] == 'updated description'


def test_patch_category_not_found(db, logged_admin_client):
    payload = {'name': 'updated name', 'description': 'updated description'}

    response = update_post(logged_admin_client, payload)
    response_data = response.json()

    expected = build_expected_error(
        detail='No Category matches the given query.', status=404, title='Not Found'
    )
    expected.update({'meta': response_data['errors'][0]['meta']})

    assert response.status_code == 404
    assert expected in response_data['errors']


@pytest.mark.parametrize(
    'payload, expected',
    [
        (
            {'invalid': 'invalid'},
            build_expected_error(detail='This field is not allowed.'),
        ),
        (
            "'{invalid json",
            build_expected_error(
                detail='Invalid JSON: Expecting value: line 1 column 1 (char 0)'
            ),
        ),
        (
            {'name': 'x' * 51},
            build_expected_error(
                'Ensure this value has at most 50 characters (it has 51).'
            ),
        ),
        ({'name': ''}, build_expected_error('This field cannot be empty or null.')),
    ],
)
def test_patch_category_validation_errors(
    db, logged_admin_client, category_factory, payload, expected
):
    category_factory.create(name='Test Category')

    response = update_post(logged_admin_client, payload)
    response_data = response.json()

    expected.update({'meta': response_data['errors'][0]['meta']})

    assert response.status_code == 400
    assert expected in response_data['errors']


def test_patch_category_generic_exception(
    db, monkeypatch, logged_admin_client, category_factory
):
    category_factory.create(name='Test Category')

    def fake_save(*args, **kwargs):
        raise Exception('Something went wrong')

    payload = {'description': 'new description'}
    monkeypatch.setattr('apps.content.views.categories.Category.save', fake_save)

    response = update_post(logged_admin_client, payload)
    response_data = response.json()

    expected = build_expected_error(
        detail='Something went wrong', status=500, title='Internal Server Error'
    )
    expected.update({'meta': response_data['errors'][0]['meta']})

    assert response.status_code == 500
    assert expected in response_data['errors']
