from django.forms.models import model_to_dict


class PostSerializer:
    @staticmethod
    def serialize_post(post, include_relationships=True):
        base_data = {
            'type': 'posts',
            'id': str(post.id),
            'attributes': {
                **model_to_dict(
                    post, exclude=['id', 'author', 'category', 'tags', 'media_files']
                ),
                'post_statistics': model_to_dict(
                    post.post_statistics, exclude=['post']
                ),
                'created_at': post.created_at,
                'updated_at': post.updated_at,
            },
        }

        if include_relationships:
            base_data['relationships'] = PostSerializer._build_relationships(post)

        return base_data

    @staticmethod
    def _build_relationships(post):
        relationships = {
            'author': {'data': [{'type': 'users', 'id': str(post.author.id)}]},
            'category': {'data': [{'type': 'categories', 'id': str(post.category.id)}]},
        }

        for rel in ['tags', 'media_files']:
            if getattr(post, rel).exists():
                relationships[rel] = {
                    'data': [
                        {'type': f'{rel}', 'id': str(obj.id)}
                        for obj in getattr(post, rel).all()
                    ]
                }

        return relationships

    @staticmethod
    def build_included_data(post):
        included = []
        included.extend(
            [
                PostSerializer._serialize_related_user(post.author),
                PostSerializer._serialize_category(post.category),
            ]
        )

        included.extend(PostSerializer._process_tags(post))
        included.extend(PostSerializer._process_media_files(post))

        return [item for item in included if item]

    @staticmethod
    def _serialize_related_user(user):
        return {
            'type': 'users',
            'id': str(user.id),
            'attributes': model_to_dict(user, fields=['username', 'role']),
        }

    @staticmethod
    def _serialize_category(category):
        data = {
            'type': 'categories',
            'id': str(category.id),
            'attributes': model_to_dict(category, exclude=['id']),
        }
        data['attributes'].update(
            {'created_at': category.created_at, 'updated_at': category.updated_at}
        )
        return data

    @staticmethod
    def _process_tags(post):
        if not post.tags.exists():
            return []

        return [
            {
                'type': 'tags',
                'id': str(tag.id),
                'attributes': {
                    'name': tag.name,
                    'slug': tag.slug,
                    'created_at': tag.created_at,
                    'updated_at': tag.updated_at,
                },
            }
            for tag in post.tags.all()
        ]

    @staticmethod
    def _process_media_files(post):
        if not post.media_files.exists():
            return []

        return [
            {
                'type': 'media_files',
                'id': str(media_file.id),
                'attributes': {
                    'file': media_file.file.name,
                    'name': media_file.name,
                    'type': media_file.type,
                    'size': media_file.size,
                    'width': media_file.width,
                    'height': media_file.height,
                    'created_at': media_file.created_at,
                    'updated_at': media_file.updated_at,
                },
            }
            for media_file in post.media_files.all()
        ]
