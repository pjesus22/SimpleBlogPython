import factory


class PostStatisticsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'content.PostStatistics'
        django_get_or_create = ('post',)

    share_count = factory.Faker('random_int', min=0, max=10_000, step=10)
    like_count = factory.Faker('random_int', min=0, max=10_000, step=10)
    comment_count = factory.Faker('random_int', min=0, max=10_000, step=10)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        post = kwargs.pop('post')
        if post is None:
            raise ValueError('Post must be provided')
        statistic, created = model_class.objects.get_or_create(post=post)
        for key, value in kwargs.items():
            setattr(statistic, key, value)
        statistic.save()
        return statistic
