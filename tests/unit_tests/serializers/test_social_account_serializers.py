from apps.users.serializers.social_accounts import SocialAccountSerializer


def test_serialize_social_accounts_includes_relationships_when_requested(
    db, author_factory, social_account_factory
):
    user = author_factory.create()
    social = social_account_factory.create(profile=user.profile)

    data = SocialAccountSerializer.serialize_social(social)

    expected = {
        'type': 'social-accounts',
        'id': str(social.pk),
        'attributes': {
            'provider': social.provider,
            'username': social.username,
            'url': social.url,
            'created_at': social.created_at,
            'updated_at': social.updated_at,
        },
        'relationships': {
            'profile': {
                'data': {'type': 'author-profiles', 'id': str(social.profile.pk)}
            }
        },
    }

    assert data == expected
