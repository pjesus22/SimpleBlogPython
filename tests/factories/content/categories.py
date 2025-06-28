import factory


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'content.Category'

    name = factory.Faker('word')
    description = factory.Faker('text', max_nb_chars=50)
