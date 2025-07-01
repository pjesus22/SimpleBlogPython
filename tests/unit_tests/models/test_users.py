import os

from apps.users.models import Admin, Author, AuthorProfile, SocialAccount


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


def test_author_profile_profile_picture_upload_path(
    db,
    author_factory,
    author_profile_factory,
    clean_media_dir,
):
    profile = author_profile_factory.create(user=author_factory.create())
    upload_path = profile.profile_picture.name
    file_name = os.path.basename(upload_path)
    expected_path = f'profiles/{file_name}'
    assert upload_path == expected_path


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
