from django.forms.models import model_to_dict


class CategorySerializer:
    @staticmethod
    def serialize_category(category, include_relationships=True):
        base_data = {
            'type': 'categories',
            'id': str(category.id),
            'attributes': {
                **model_to_dict(category, exclude=['id', 'posts']),
                'created_at': category.created_at,
                'updated_at': category.updated_at,
            },
        }
        if include_relationships:
            base_data['relationships'] = CategorySerializer._build_relationships(
                category
            )
        return base_data

    @staticmethod
    def _build_relationships(category):
        relationships = {}
        if category.posts.exists():
            relationships['posts'] = {
                'data': [
                    {'type': 'posts', 'id': str(post.id)}
                    for post in category.posts.all()
                ]
            }
        return relationships

    @staticmethod
    def build_included_data(category):
        included = []
        if category.posts.exists():
            included.extend(CategorySerializer._process_posts(category))
        return [item for item in included if item]

    @staticmethod
    def _process_posts(category):
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
            for post in category.posts.all()
        ]
