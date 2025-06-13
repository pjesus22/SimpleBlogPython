class AuthorProfileSerializer:
    @staticmethod
    def serialize_profile(profile, include_relationships=True):
        base_data = {
            'type': 'author-profiles',
            'id': str(profile.user.pk),
            'attributes': {
                'bio': profile.bio,
                'profile_picture': profile.profile_picture.name
                if profile.profile_picture
                else None,
            },
        }
        if include_relationships:
            base_data['relationships'] = {}
            if profile.social_accounts.exists():
                base_data['relationships']['social-accounts'] = {
                    'data': [
                        {
                            'type': 'social-accounts',
                            'id': str(social.id),
                        }
                        for social in profile.social_accounts.all()
                    ]
                }
        return base_data
