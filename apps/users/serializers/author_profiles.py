class AuthorProfileSerializer:
    @staticmethod
    def serialize_profile(profile, include_relationships=True):
        base_data = {
            'type': 'author-profiles',
            'id': str(profile.user.pk),
            'attributes': {
                'bio': profile.bio,
            },
        }
        if include_relationships:
            base_data['relationships'] = {}
            if profile.social_accounts.exists():
                base_data['relationships']['social_accounts'] = {
                    'data': [
                        {
                            'type': 'social-accounts',
                            'id': str(social.id),
                        }
                        for social in profile.social_accounts.all()
                    ]
                }
        return base_data
