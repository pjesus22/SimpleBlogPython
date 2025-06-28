from pathlib import Path

import pytest
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.files.base import ContentFile

from apps.media_files.models import MediaFile


@pytest.fixture
def new_media_file(db, media_file_factory, clean_media_dir):
    path = Path('tests/mock_data/alpaca.png')
    with path.open(mode='rb') as f:
        media_file = media_file_factory.create(file=File(f, name=path.name))
    return media_file


def test_media_file_str():
    media_file = MediaFile(
        name='Test Media File',
        file=File(ContentFile(b'fake content'), name='test_media_file.png'),
    )
    assert str(media_file) == media_file.name


def test_media_file_returns_correct_file_type(new_media_file):
    assert new_media_file.type == 'image'


def test_media_file_returns_metadata(new_media_file):
    assert new_media_file.width > 0
    assert new_media_file.height > 0


def test_raise_error_if_invalid_file_type(db, media_file_factory):
    with pytest.raises(ValidationError) as excinfo:
        media_file_factory.create(file=ContentFile(b'fake file', name='fake.txt'))

    assert 'Invalid file type: .txt is not allowed.' in str(excinfo.value)


def test_raise_error_if_invalid_image_file(db, media_file_factory):
    with pytest.raises(ValidationError) as excinfo:
        media_file_factory.create(file=ContentFile(b'fake image', name='fake.png'))

    assert 'Error extracting image metadata' in str(excinfo.value)


def test_raise_validation_error_if_duplicate_name_for_same_post(
    db, media_file_factory, post_factory
):
    post = post_factory.create(title='Test Post')
    path = Path('tests/mock_data/alpaca.png')
    with path.open(mode='rb') as f:
        original_media = media_file_factory.create(
            file=File(f, name=path.name), post=post
        )

    with path.open(mode='rb') as f:
        duplicate_media = media_file_factory.build(
            file=File(f, name=path.name), post=post
        )
        duplicate_media.name = original_media.name

        with pytest.raises(ValidationError) as excinfo:
            duplicate_media.clean()

        assert (
            f"A file with name '{original_media.name}' already exists for this post."
            in str(excinfo.value)
        )
