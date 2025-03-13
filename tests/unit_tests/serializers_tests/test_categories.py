import pytest

from apps.content.serializers import CategorySerializer

pytestmark = pytest.mark.django_db


@pytest.fixture
def category_inst(category_factory, post_factory):
    category = category_factory.create(
        name='Test category',
        description='Test description',
    )
    post_factory.create_batch(size=3, category=category)
    return category


def test_serialize_category_includes_relationships_when_requested(category_inst):
    serialized_data = CategorySerializer.serialize_category(
        category_inst, include_relationships=True
    )
    expected_data = {
        'posts': {
            'data': [
                {'type': 'posts', 'id': str(post.pk)}
                for post in category_inst.posts.all()
            ]
        }
    }

    assert 'relationships' in serialized_data
    assert serialized_data['relationships'] == expected_data


def test_serialize_category_excludes_relationships_when_not_requested(category_inst):
    serialized_data = CategorySerializer.serialize_category(
        category_inst, include_relationships=False
    )

    assert 'relationships' not in serialized_data


def test_build_included_data_includes_correct_post_details(category_inst):
    included = CategorySerializer.build_included_data(category_inst)
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
        for post in category_inst.posts.all()
    ]
    assert len(included) == len(expected_posts)
    for expected_post in expected_posts:
        assert expected_post in included
