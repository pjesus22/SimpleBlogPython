import factory
from django.utils.text import slugify


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'content.Tag'

    name = factory.Faker('word')
    slug = factory.LazyAttribute(lambda o: slugify(o.name))
