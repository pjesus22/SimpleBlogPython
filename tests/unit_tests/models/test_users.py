import os

import pytest

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_inst(admin_factory):
    return admin_factory.create(username='test_admin')


@pytest.fixture
def author_profile_inst(author_profile_factory, author_inst):
    return author_profile_factory.create(user=author_inst)


@pytest.fixture
def author_inst(author_factory):
    return author_factory.create(username='test_author')


def test_admin_str_(admin_inst):
    assert admin_inst.__str__() == f'{admin_inst.username} ({admin_inst.role})'


def test_author_str_(author_inst):
    assert author_inst.__str__() == f'{author_inst.username} ({author_inst.role})'


def test_author_profile_str_(author_profile_inst):
    assert (
        author_profile_inst.__str__()
        == f'{author_profile_inst.user.username} ({author_profile_inst.user.role}) profile'
    )


def test_author_profile_profile_picture_upload_path(author_profile_inst):
    upload_path = author_profile_inst.profile_picture.name
    file_name = os.path.basename(upload_path)
    expected_path = f'{author_profile_inst.user.id}/image/profile/{file_name}'
    assert upload_path == expected_path


def test_social_account_str_(
    social_account_factory, author_profile_inst, clean_media_dir
):
    social_account = social_account_factory.create(profile=author_profile_inst)
    assert (
        social_account.__str__()
        == f'{social_account.username} ({social_account.provider})'
    )
