import factory
from django.utils.text import slugify

from apps.content.models import Post

from ..users import AuthorFactory
from .categories import CategoryFactory


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'content.Post'
        skip_postgeneration_save = True

    author = factory.SubFactory(AuthorFactory)
    category = factory.SubFactory(CategoryFactory)
    title = factory.Faker('sentence', nb_words=6)
    content = factory.Faker('text', max_nb_chars=500)
    status = factory.Faker(
        'random_element', elements=[x[0] for x in Post.Status.choices]
    )

    @factory.lazy_attribute
    def slug(self):
        return slugify(self.title)

    @factory.post_generation
    def media_files(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.media_files.add(*extracted)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create or not extracted:
            return
        self.tags.add(*extracted)
