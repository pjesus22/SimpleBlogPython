from apps.users.serializers.author_profiles import AuthorProfileSerializer


def test_serialize_profile_includes_relationships_when_requested(
    db, author_profile_factory, author_factory, social_account_factory
):
    user = author_factory.create()
    profile = user.profile

    author_profile_factory.create(user=user)
    social_account_factory.create(profile=profile)

    profile.refresh_from_db()

    data = AuthorProfileSerializer.serialize_profile(profile)

    expected = {
        'type': 'author-profiles',
        'id': str(profile.pk),
        'attributes': {
            'bio': profile.bio,
            'profile_picture': profile.profile_picture.name,
        },
        'relationships': {
            'social_accounts': {
                'data': [
                    {'type': 'social-accounts', 'id': str(social.pk)}
                    for social in profile.social_accounts.all()
                ]
            }
        },
    }

    assert data == expected
