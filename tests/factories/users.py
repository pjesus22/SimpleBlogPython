import factory
from django.contrib.auth.hashers import make_password
from faker import Faker

from apps.users.models import Admin, Author, AuthorProfile, User

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'users.User'

    class Params:
        plain_password = 'password'

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    password = factory.LazyAttribute(lambda o: make_password(o.plain_password))
    role = User.Role.ADMIN


class AdminFactory(UserFactory):
    class Meta:
        model = Admin


class AuthorFactory(UserFactory):
    class Meta:
        model = Author

    role = User.Role.AUTHOR


class AuthorProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AuthorProfile
        django_get_or_create = ('user',)

    profile_picture = factory.django.ImageField(color='red')
    bio = factory.Faker('text', max_nb_chars=500)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        user = kwargs.pop('user', None)
        if user is None:
            raise ValueError('User must be provided')
        author_profile, created = AuthorProfile.objects.get_or_create(user=user)
        for key, value in kwargs.items():
            setattr(author_profile, key, value)
        author_profile.save()
        return author_profile


class SocialAccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'users.SocialAccount'

    provider = factory.Faker('company')
    username = factory.Faker('company')
    url = factory.Faker('url')
    profile = factory.SubFactory(AuthorProfileFactory)
