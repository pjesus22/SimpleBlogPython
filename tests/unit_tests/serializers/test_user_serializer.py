from apps.users.serializers import UserSerializer


def test_serialize_user_includes_relationships_when_requested(
    db, author_factory, post_factory
):
    user = author_factory.create()
    post_factory.create_batch(size=2, author=user)
    data = UserSerializer.serialize_user(user, include_relationships=True)
    expected = {
        'profile': {'data': {'type': 'author-profiles', 'id': str(user.profile.pk)}},
        'posts': {
            'data': [{'type': 'posts', 'id': str(post.id)} for post in user.posts.all()]
        },
    }

    assert 'relationships' in data
    assert data['relationships'] == expected


def test_serialize_user_excludes_relationships_when_not_requested(db, author_factory):
    user = author_factory.create()
    data = UserSerializer.serialize_user(user, include_relationships=False)

    assert 'relationships' not in data


def test_build_included_data_includes_correct_post_details(
    db, author_factory, social_account_factory, post_factory, author_profile_factory
):
    user = author_factory.create()
    profile = author_profile_factory.create(user=user)
    social_account_factory.create_batch(size=2, profile=profile)
    post_factory.create_batch(size=2, author=user)

    user.refresh_from_db()

    included = UserSerializer.build_included_data(user)

    expected = []

    expected.extend(
        [
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
            for post in user.posts.all()
        ]
    )

    expected.append(
        {
            'type': 'author-profiles',
            'id': str(profile.user.pk),
            'attributes': {
                'bio': profile.bio,
                'profile_picture': profile.profile_picture.name,
            },
            'relationships': {
                'social_accounts': {
                    'data': [
                        {
                            'type': 'social-accounts',
                            'id': str(social.pk),
                        }
                        for social in user.profile.social_accounts.all()
                    ]
                }
            },
        }
    )

    expected.extend(
        [
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
            for social in user.profile.social_accounts.all()
        ]
    )

    included_set = {str(item) for item in included}
    expected_set = {str(item) for item in expected}

    assert len(included) == len(expected)
    assert expected_set.issubset(included_set)
