# utils/serializers.py
from django.forms.models import model_to_dict


class TagSerializer:
    @staticmethod
    def serialize_tag(tag, include_relationships=True):
        base_data = {
            'type': 'tags',
            'id': str(tag.id),
            'attributes': {
                **model_to_dict(tag, exclude=['id']),
                'created_at': tag.created_at,
                'updated_at': tag.updated_at,
            },
        }

        if include_relationships:
            base_data['relationships'] = TagSerializer._build_relationships(tag)

        return base_data

    @staticmethod
    def _build_relationships(tag):
        relationships = {}
        if tag.posts.exists():
            relationships['posts'] = {
                'data': [
                    {'type': 'posts', 'id': str(post.id)} for post in tag.posts.all()
                ]
            }

        return relationships

    @staticmethod
    def build_included_data(tag):
        included = []
        if tag.posts.exists():
            included.extend(TagSerializer._process_posts(tag))

        return [item for item in included if item]

    @staticmethod
    def _process_posts(tag):
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
            for post in tag.posts.all()
        ]
