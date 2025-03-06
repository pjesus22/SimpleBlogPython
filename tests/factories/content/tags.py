import factory


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'content.Tag'

    name = factory.Faker('word')
