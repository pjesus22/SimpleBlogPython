import os
from pathlib import Path

import pytest
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.base import ContentFile

pytestmark = pytest.mark.django_db


@pytest.fixture
def category_inst(category_factory):
    return category_factory.create(name='Test Category')


@pytest.fixture
def post_inst(post_factory):
    return post_factory.create(title='Test Post')


@pytest.fixture
def tag_inst(tag_factory):
    return tag_factory.create(name='Test Tag')


@pytest.fixture
def media_file_inst(media_file_factory, clean_media_dir):
    path = Path('tests/mock_data/alpaca.png')
    with path.open(mode='rb') as f:
        media_file = media_file_factory.create(file=File(f, name=path.name))
    return media_file


@pytest.fixture
def admin_inst(admin_factory):
    return admin_factory.create(username='test_admin')


@pytest.fixture
def author_profile_inst(author_profile_factory, author_inst):
    return author_profile_factory.create(user=author_inst)


@pytest.fixture
def author_inst(author_factory):
    return author_factory.create(username='test_author')


class TestCategories:
    def test_category_str_(self, category_inst):
        assert category_inst.__str__() == category_inst.name

    def test_category_slug_generated_on_save(self, category_inst):
        assert category_inst.slug == 'test-category'


class TestPosts:
    def test_post_str_(self, post_inst):
        assert post_inst.__str__() == post_inst.title

    def test_post_slug_generated_on_save(self, post_inst):
        assert post_inst.slug == 'test-post'


class TestTags:
    def test_tag_str_(self, tag_inst):
        assert tag_inst.__str__() == tag_inst.name

    def test_tag_slug_generated_on_save(self, tag_inst):
        assert tag_inst.slug == 'test-tag'


class TestMediaFiles:
    def test_media_file_str_(self, media_file_inst):
        assert media_file_inst.__str__() == media_file_inst.name

    def test_media_file_returns_correct_file_type(self, media_file_inst):
        assert media_file_inst.type == 'image'

    def test_media_file_returns_metadata(self, media_file_inst):
        assert media_file_inst.width > 0
        assert media_file_inst.height > 0

    def test_raise_error_if_invalid_file_type(self, media_file_factory):
        with pytest.raises(ValidationError) as excinfo:
            media_file_factory.create(file=ContentFile(b'fake file', name='fake.txt'))

        assert 'Invalid file type: .txt is not allowed.' in str(excinfo.value)

    def test_raise_error_if_invalid_image_file(self, media_file_factory):
        with pytest.raises(ValidationError) as excinfo:
            media_file_factory.create(file=ContentFile(b'fake image', name='fake.png'))

        assert 'Error extracting image metadata' in str(excinfo.value)


class TestUsers:
    def test_admin_str_(self, admin_inst):
        assert admin_inst.__str__() == f'{admin_inst.username} ({admin_inst.role})'

    def test_author_str_(self, author_inst):
        assert author_inst.__str__() == f'{author_inst.username} ({author_inst.role})'

    def test_author_profile_str_(self, author_profile_inst):
        assert (
            author_profile_inst.__str__()
            == f'{author_profile_inst.user.username} ({author_profile_inst.user.role}) profile'
        )

    def test_author_profile_profile_picture_upload_path(self, author_profile_inst):
        upload_path = author_profile_inst.profile_picture.name
        file_name = os.path.basename(upload_path)
        expected_path = f'{author_profile_inst.user.id}/image/profile/{file_name}'
        assert upload_path == expected_path

    def test_social_account_str_(
        self, social_account_factory, author_profile_inst, clean_media_dir
    ):
        social_account = social_account_factory.create(profile=author_profile_inst)
        assert (
            social_account.__str__()
            == f'{social_account.username} ({social_account.provider})'
        )
