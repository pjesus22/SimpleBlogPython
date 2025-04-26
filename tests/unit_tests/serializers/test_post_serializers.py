import pytest

from apps.content.serializers import PostSerializer

pytestmark = pytest.mark.django_db


@pytest.fixture
def post_inst(
    author_factory,
    post_factory,
    category_factory,
    tag_factory,
    media_file_factory,
    post_statistics_factory,
    clean_media_dir,
):
    user = author_factory()
    category = category_factory()
    tags = tag_factory.create_batch(size=3)
    media_files = media_file_factory.create_batch(size=2)
    post = post_factory(
        author=user,
        category=category,
        tags=tags,
        media_files=media_files,
    )
    post_statistics = post_statistics_factory(post=post)  # NOQA: F841
    return post


@pytest.fixture
def post_inst_without_tags_or_media_files(
    author_factory,
    post_factory,
    category_factory,
    post_statistics_factory,
    clean_media_dir,
):
    user = author_factory()
    category = category_factory()
    post = post_factory(
        author=user,
        category=category,
    )
    post_statistics = post_statistics_factory(post=post)  # NOQA: F841
    return post


def test_serialize_post_includes_relationships_when_requested(post_inst):
    serialized_data = PostSerializer.serialize_post(
        post_inst, include_relationships=True
    )
    expected_data = {
        'author': {'data': {'type': 'users', 'id': str(post_inst.author.pk)}},
        'category': {'data': {'type': 'categories', 'id': str(post_inst.category.pk)}},
        'tags': {
            'data': [
                {'type': 'tags', 'id': str(tag.pk)} for tag in post_inst.tags.all()
            ]
        },
        'media_files': {
            'data': [
                {'type': 'media_files', 'id': str(media_file.pk)}
                for media_file in post_inst.media_files.all()
            ]
        },
    }

    assert 'relationships' in serialized_data
    assert serialized_data['relationships'] == expected_data


def test_serialize_post_excludes_relationships_when_not_requested(post_inst):
    serialized_data = PostSerializer.serialize_post(
        post_inst, include_relationships=False
    )

    assert 'relationships' not in serialized_data


def test_build_included_data_includes_correct_post_details(post_inst):
    included = PostSerializer.build_included_data(post_inst)
    expected_tags = [
        {
            'type': 'tags',
            'id': str(tag.pk),
            'attributes': {
                'name': tag.name,
                'slug': tag.slug,
                'created_at': tag.created_at,
                'updated_at': tag.updated_at,
            },
        }
        for tag in post_inst.tags.all()
    ]
    expected_media_files = [
        {
            'type': 'media_files',
            'id': str(media_file.pk),
            'attributes': {
                'file': media_file.file.name,
                'name': media_file.name,
                'type': media_file.type,
                'size': media_file.size,
                'width': media_file.width,
                'height': media_file.height,
                'created_at': media_file.created_at,
                'updated_at': media_file.updated_at,
            },
        }
        for media_file in post_inst.media_files.all()
    ]
    expected_author = {
        'type': 'users',
        'id': str(post_inst.author.pk),
        'attributes': {
            'username': post_inst.author.username,
            'role': post_inst.author.role,
        },
    }
    expected_category = {
        'type': 'categories',
        'id': str(post_inst.category.pk),
        'attributes': {
            'name': post_inst.category.name,
            'description': post_inst.category.description,
            'slug': post_inst.category.slug,
            'created_at': post_inst.category.created_at,
            'updated_at': post_inst.category.updated_at,
        },
    }

    for expected_tag in expected_tags:
        assert expected_tag in included

    for expected_media_file in expected_media_files:
        assert expected_media_file in included

    assert expected_author in included

    assert expected_category in included

    expected_length = len(expected_tags) + len(expected_media_files) + 2
    assert len(included) == expected_length


def test_build_included_data_excludes_tags_and_media_files_when_not_requested(
    post_inst_without_tags_or_media_files,
):
    included = PostSerializer.build_included_data(post_inst_without_tags_or_media_files)
    expected_length = 2
    assert len(included) == expected_length
