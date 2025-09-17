import pytest
from django.core.exceptions import ValidationError

from apps.users.models import Admin, Author, AuthorProfile, SocialAccount, User


def test_admin_str_():
    user = Admin(username='testAdmin')
    assert str(user) == f'{user.username} ({user.role})'


def test_admin_manager(db, admin_factory):
    admin_factory.create(username='test_admin')
    assert Admin.objects.get(username='test_admin')


def test_author_str_():
    user = Author(username='testAuthor')
    assert str(user) == f'{user.username} ({user.role})'


def test_author_profile_str_():
    user = Author(username='testAuthor')
    profile = AuthorProfile(user=user, bio='Test bio')
    assert str(profile) == f'{profile.user.username} ({profile.user.role}) profile'


def test_social_account_str_():
    profile = AuthorProfile(user=Author(username='testAuthor'))
    social_account = SocialAccount(
        provider='testProvider',
        username='testUser',
        url='https://example.com/testUser',
        profile=profile,
    )
    assert (
        str(social_account) == f'{social_account.username} ({social_account.provider})'
    )


@pytest.mark.parametrize(
    'field,invalid_value',
    [
        ('username', ''),
        ('username', None),
        ('email', ''),
        ('email', None),
        ('password', ''),
        ('password', None),
    ],
)
def test_required_fields_cannot_be_empty(db, field, invalid_value):
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'ValidPassword123',
    }
    user_data[field] = invalid_value

    user = User(**user_data)

    with pytest.raises(ValidationError) as excinfo:
        user.clean()

    errors = excinfo.value.message_dict
    assert field in errors
    assert 'This field cannot be empty or null.' in errors[field][0]
