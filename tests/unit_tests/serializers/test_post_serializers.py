import pytest

from apps.content.serializers import PostSerializer

pytestmark = pytest.mark.django_db


@pytest.fixture
def new_post(post_factory):
    return post_factory()


def test_serialize_post_includes_relationships_when_requested(new_post):
    data = PostSerializer.serialize_post(new_post, include_relationships=True)
    expected = {
        'author': {
            'data': {
                'type': 'users',
                'id': str(new_post.author.pk),
            }
        },
        'category': {
            'data': {
                'type': 'categories',
                'id': str(new_post.category.pk),
            }
        },
        'statistics': {
            'data': {
                'type': 'post_statistics',
                'id': str(new_post.post_statistics.pk),
            }
        },
    }

    assert 'relationships' in data
    assert all(key in data['relationships'] for key in expected.keys())


def test_serialize_post_excludes_relationships_when_not_requested(new_post):
    data = PostSerializer.serialize_post(new_post, include_relationships=False)

    assert 'relationships' not in data


@pytest.mark.parametrize(
    'tag_count, media_file_count',
    [
        (2, 2),
        (0, 0),
        (0, 2),
        (2, 0),
    ],
    ids=[
        'tags_and_media_files',
        'none',
        'only_media_files',
        'only_tags',
    ],
)
def test_build_included_data_includes_correct_post_details(
    post_factory, tag_factory, media_file_factory, tag_count, media_file_count
):
    tags = tag_factory.create_batch(size=tag_count) if tag_count > 0 else []
    media_files = (
        media_file_factory.create_batch(size=2) if media_file_count > 0 else []
    )
    post = post_factory(tags=tags, media_files=media_files)
    included = PostSerializer.build_included_data(post)
    data = PostSerializer.serialize_post(post, include_relationships=True)

    expected_items = []

    expected_items.append(
        {
            'type': 'users',
            'id': str(post.author.pk),
            'attributes': {
                'username': post.author.username,
                'role': post.author.role,
            },
        }
    )

    expected_items.append(
        {
            'type': 'categories',
            'id': str(post.category.pk),
            'attributes': {
                'name': post.category.name,
                'description': post.category.description,
                'slug': post.category.slug,
                'created_at': post.category.created_at,
                'updated_at': post.category.updated_at,
            },
        }
    )

    expected_items.append(
        {
            'type': 'post_statistics',
            'id': str(post.post_statistics.pk),
            'attributes': {
                'share_count': post.post_statistics.share_count,
                'like_count': post.post_statistics.like_count,
                'comment_count': post.post_statistics.comment_count,
                'created_at': post.post_statistics.created_at,
                'updated_at': post.post_statistics.updated_at,
            },
        }
    )

    if tag_count > 0 or media_file_count > 0:
        expected_items.extend(
            [
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
                for tag in tags
            ]
        )

        expected_items.extend(
            [
                {
                    'type': 'media_files',
                    'id': str(media_file.pk),
                    'attributes': {
                        'file': str(media_file.file.url),
                        'type': media_file.type.value,
                        'created_at': media_file.created_at,
                        'updated_at': media_file.updated_at,
                    },
                }
                for media_file in media_files
            ]
        )

    included_set = {str(item) for item in included}
    expected_set = {str(item) for item in expected_items}

    if tag_count:
        tag_ids = {str(tag.id) for tag in tags}
        rel_tag_ids = {item['id'] for item in data['relationships']['tags']['data']}
        assert tag_ids == rel_tag_ids
    if media_file_count:
        mf_ids = {str(mf.id) for mf in media_files}
        rel_mf_ids = {
            item['id'] for item in data['relationships']['media_files']['data']
        }
        assert mf_ids == rel_mf_ids

    assert expected_set.issubset(included_set)
    assert len(included) == len(expected_items)
