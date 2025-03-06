import factory


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'content.Category'

    name = factory.Faker('word')
    description = factory.Faker('paragraph', nb_sentences=3)
