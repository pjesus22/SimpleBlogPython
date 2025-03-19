class MediaFileSerializer:
    @staticmethod
    def serialize_media_file(media_file, include_relationships=True):
        base_data = {
            'type': 'media_files',
            'id': str(media_file.id),
            'attributes': {
                'name': media_file.name,
                'file': media_file.file.url,
                'type': media_file.type,
                'size': media_file.size,
                'width': media_file.width,
                'height': media_file.height,
                'created_at': media_file.created_at,
                'updated_at': media_file.updated_at,
            },
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
    def serialize_media_files(media_files, include_relationships=True):
        return [
            MediaFileSerializer.serialize_media_file(media_file, include_relationships)
            for media_file in media_files
        ]
