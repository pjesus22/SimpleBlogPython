from pathlib import Path

import pytest
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.base import ContentFile

pytestmark = pytest.mark.django_db


@pytest.fixture
def post_inst(post_factory):
    return post_factory.create(title='Test Post')


@pytest.fixture
def media_file_inst(media_file_factory, clean_media_dir):
    path = Path('tests/mock_data/alpaca.png')
    with path.open(mode='rb') as f:
        media_file = media_file_factory.create(file=File(f, name=path.name))
    return media_file


def test_media_file_str_(media_file_inst):
    assert media_file_inst.__str__() == media_file_inst.name


def test_media_file_returns_correct_file_type(media_file_inst):
    assert media_file_inst.type == 'image'


def test_media_file_returns_metadata(media_file_inst):
    assert media_file_inst.width > 0
    assert media_file_inst.height > 0


def test_raise_error_if_invalid_file_type(media_file_factory):
    with pytest.raises(ValidationError) as excinfo:
        media_file_factory.create(file=ContentFile(b'fake file', name='fake.txt'))

    assert 'Invalid file type: .txt is not allowed.' in str(excinfo.value)


def test_raise_error_if_invalid_image_file(media_file_factory):
    with pytest.raises(ValidationError) as excinfo:
        media_file_factory.create(file=ContentFile(b'fake image', name='fake.png'))

    assert 'Error extracting image metadata' in str(excinfo.value)


def test_raise_validation_error_if_duplicate_name_for_same_post(
    media_file_factory, post_inst
):
    path = Path('tests/mock_data/alpaca.png')
    with path.open(mode='rb') as f:
        original_media = media_file_factory.create(
            file=File(f, name=path.name), post=post_inst
        )

    with path.open(mode='rb') as f:
        duplicate_media = media_file_factory.build(
            file=File(f, name=path.name), post=post_inst
        )
        duplicate_media.name = original_media.name

        with pytest.raises(ValidationError) as excinfo:
            duplicate_media.clean()

        assert (
            f"A file with name '{original_media.name}' already exists for this post."
            in str(excinfo.value)
        )
