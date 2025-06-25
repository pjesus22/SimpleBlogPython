from django.http import Http404

from apps.content.models.tags import Tag


def validate_required_fields(data, required_fields) -> None:
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        raise ValueError(f'Missing required fields: {", ".join(missing)}')


def validate_invalid_fields(data, allowed_fields) -> None:
    invalid_fields = set(data.keys()) - set(allowed_fields)
    if invalid_fields:
        raise ValueError(f'Invalid fields: {", ".join(invalid_fields)}')


def get_valid_tags_or_404(tag_slugs):
    if not isinstance(tag_slugs, (list, set, tuple)):
        raise ValueError('"tags" must be a list.')
    tag_slugs = set(tag_slugs)
    tags = {tag.slug: tag for tag in Tag.objects.filter(slug__in=tag_slugs)}
    missing = tag_slugs - tags.keys()
    if missing:
        raise Http404(f'Tags not found: {", ".join(missing)}')
    return tags
