import pytest

from apps.users.serializers import UserSerializer

pytestmark = pytest.mark.django_db


@pytest.fixture
def user_inst(
    author_factory, post_factory, social_account_factory, author_profile_factory
):
    user = author_factory(
        username='admin',
        email='admin@admin.com',
        is_superuser=True,
        is_staff=True,
        is_active=True,
        first_name='Admin',
        last_name='Admin',
    )
    post_factory.create_batch(size=3, author=user)
    profile = author_profile_factory.create(user=user)
    social_account_factory.create_batch(size=3, profile=profile)
    return user


def test_serialize_user_includes_relationships_when_requested(user_inst):
    serialized_data = UserSerializer.serialize_user(
        user_inst, include_relationships=True
    )
    expected_data = {
        'posts': {
            'data': [
                {'type': 'posts', 'id': str(post.pk)} for post in user_inst.posts.all()
            ]
        },
        'profile': {
            'data': {'type': 'author-profiles', 'id': str(user_inst.profile.pk)}
        },
    }

    assert 'relationships' in serialized_data
    assert serialized_data['relationships'] == expected_data


def test_serialize_user_excludes_relationships_when_not_requested(user_inst):
    serialized_data = UserSerializer.serialize_user(
        user_inst, include_relationships=False
    )

    assert 'relationships' not in serialized_data


def test_build_included_data_includes_correct_post_details(user_inst):
    included = UserSerializer.build_included_data(user_inst)
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
        for post in user_inst.posts.all()
    ]
    expected_profile = {  # NOQA F841
        'type': 'author-profiles',
        'id': str(user_inst.profile.pk),
        'attributes': {
            'bio': user_inst.profile.bio,
            'profile_picture': user_inst.profile.profile_picture.name,
        },
        'relationships': {
            'social-accounts': {
                'data': [
                    {
                        'type': 'social_accounts',
                        'id': str(social.pk),
                    }
                    for social in user_inst.profile.social_accounts.all()
                ]
            }
        }
        if user_inst.profile.social_accounts.exists()
        else {},
    }

    expected_social_accounts = [
        {
            'type': 'social-accounts',
            'id': str(social.pk),
            'attributes': {
                'provider': social.provider,
                'username': social.username,
                'url': social.url,
                'created_at': social.created_at,
                'updated_at': social.updated_at,
            },
        }
        for social in user_inst.profile.social_accounts.all()
    ]

    for expected_social in expected_social_accounts:
        assert expected_social in included

    for expected_post in expected_posts:
        assert expected_post in included

    expected_length = len(expected_posts) + len(expected_social_accounts) + 1
    assert len(included) == expected_length
