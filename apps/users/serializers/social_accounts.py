class SocialAccountSerializer:
    @staticmethod
    def serialize_social(social, include_relationships=True):
        base_data = {
            'type': 'social-accounts',
            'id': str(social.id),
            'attributes': {
                'provider': social.provider,
                'username': social.username,
                'url': social.url,
                'created_at': social.created_at
                if hasattr(social, 'created_at')
                else None,
                'updated_at': social.updated_at
                if hasattr(social, 'updated_at')
                else None,
            },
        }
        if include_relationships:
            base_data['relationships'] = {
                'profile': {
                    'data': {
                        'type': 'author-profiles',
                        'id': str(social.profile.user.pk),
                    }
                }
            }
        return base_data
