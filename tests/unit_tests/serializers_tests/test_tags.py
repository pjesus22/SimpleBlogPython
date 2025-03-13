import pytest

from apps.content.serializers import TagSerializer

pytestmark = pytest.mark.django_db


@pytest.fixture
def tag_inst(tag_factory, post_factory):
    tag = tag_factory.create(name='Test tag')
    post_factory.create_batch(size=3, tags=[tag])
    return tag


def test_serialize_tag_includes_relationships_when_requested(tag_inst):
    serialized_data = TagSerializer.serialize_tag(tag_inst, include_relationships=True)
    expected_data = {
        'posts': {
            'data': [
                {'type': 'posts', 'id': str(post.pk)} for post in tag_inst.posts.all()
            ]
        }
    }

    assert 'relationships' in serialized_data
    assert serialized_data['relationships'] == expected_data


def test_serialize_tag_excludes_relationships_when_not_requested(tag_inst):
    serialized_data = TagSerializer.serialize_tag(tag_inst, include_relationships=False)

    assert 'relationships' not in serialized_data


def test_build_included_data_includes_correct_post_details(tag_inst):
    included = TagSerializer.build_included_data(tag_inst)
    expected_posts = [
        {
            'type': 'posts',
            'id': str(post.pk),
            'attributes': {
                'title': post.title,
                'slug': post.slug,
                'content': post.content,
                'status': post.status,
                'created_at': post.created_at,
                'updated_at': post.updated_at,
            },
        }
        for post in tag_inst.posts.all()
    ]
    assert len(included) == len(expected_posts)
    for expected_post in expected_posts:
        assert expected_post in included
