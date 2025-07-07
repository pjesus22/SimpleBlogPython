from django.core.exceptions import ValidationError
from django.http import Http404

from apps.content.models.tags import Tag


def validate_required_fields(data, required_fields) -> None:
    missing = [
        field for field in required_fields if field not in data or data[field] is None
    ]
    if missing:
        message_dict = {field: ['This field is required.'] for field in missing}
        raise ValidationError(message_dict, code='missing_fields')


def validate_invalid_fields(data, allowed_fields) -> None:
    invalid_fields = [field for field in data if field not in allowed_fields]
    if invalid_fields:
        message_dict = {
            field: ['This field is not allowed.'] for field in invalid_fields
        }
        raise ValidationError(message_dict, code='invalid_fields')


def get_valid_tags_or_404(tag_slugs):
    if not isinstance(tag_slugs, (list, set, tuple)):
        raise ValueError('"tags" must be a list.')
    tag_slugs = set(tag_slugs)
    tags = {tag.slug: tag for tag in Tag.objects.filter(slug__in=tag_slugs)}
    missing = tag_slugs - tags.keys()
    if missing:
        raise Http404(f'Tags not found: {", ".join(missing)}')
    return tags
