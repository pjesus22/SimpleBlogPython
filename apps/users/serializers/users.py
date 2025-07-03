from django.forms.models import model_to_dict


class UserSerializer:
    @staticmethod
    def serialize_user(user, include_relationships=True):
        base_data = {
            'type': 'users',
            'id': str(user.id),
            'attributes': {
                **model_to_dict(
                    user,
                    fields=[
                        'username',
                        'email',
                        'first_name',
                        'last_name',
                        'role',
                        'is_active',
                        'date_joined',
                    ],
                ),
            },
        }
        if include_relationships:
            base_data['relationships'] = UserSerializer._build_relationships(user)
        return base_data

    @staticmethod
    def _build_relationships(user):
        relationships = {}

        if hasattr(user, 'profile'):
            relationships['profile'] = {
                'data': {'type': 'author-profiles', 'id': str(user.profile.pk)}
            }

        if user.posts.exists():
            relationships['posts'] = {
                'data': [
                    {'type': 'posts', 'id': str(post.id)} for post in user.posts.all()
                ]
            }
        return relationships

    @staticmethod
    def build_included_data(user):
        included = []

        if hasattr(user, 'profile'):
            included.append(UserSerializer._serialize_profile(user.profile))

            if user.profile.social_accounts.exists():
                included.extend(
                    UserSerializer._serialize_social_accounts(
                        user.profile.social_accounts.all()
                    )
                )

        if user.posts.exists():
            included.extend(UserSerializer._serialize_related_posts(user))

        return included

    @staticmethod
    def _serialize_related_posts(user):
        return [
            {
                'type': 'posts',
                'id': str(post.id),
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

    @staticmethod
    def _serialize_profile(profile):
        base_data = {
            'type': 'author-profiles',
            'id': str(profile.user.pk),
            'attributes': {
                'bio': profile.bio,
                'profile_picture': profile.profile_picture.name,
            },
            'relationships': {},
        }

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

    @staticmethod
    def _serialize_social_accounts(social_accounts):
        return [
            {
                'type': 'social-accounts',
                'id': str(social.id),
                'attributes': {
                    'provider': social.provider,
                    'username': social.username,
                    'url': social.url,
                    'created_at': social.created_at,
                    'updated_at': social.updated_at,
                },
            }
            for social in social_accounts
        ]
