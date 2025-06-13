class MediaFileSerializer:
    @staticmethod
    def serialize_media_file(media_file, include_relationships=True, public=False):
        attributes = {
            'type': media_file.type,
            'file': media_file.file.url,
            'created_at': media_file.created_at,
            'updated_at': media_file.updated_at,
        }

        if not public:
            attributes.update(
                {
                    'name': media_file.name,
                    'size': media_file.size,
                    'width': media_file.width,
                    'height': media_file.height,
                }
            )

        base_data = {
            'type': 'media_files',
            'id': str(media_file.id),
            'attributes': attributes,
        }

        if include_relationships:
            base_data['relationships'] = {
                'post': {
                    'data': {
                        'type': 'posts',
                        'id': str(media_file.post.id),
                    }
                }
            }

        return base_data

    @staticmethod
    def serialize_media_files(media_files, include_relationships=True, public=False):
        return [
            MediaFileSerializer.serialize_media_file(
                media_file, include_relationships, public=public
            )
            for media_file in media_files
        ]
