from apps.content.models import Category, Post, Tag


def test_category_str():
    category = Category(
        name='Test Category',
        description='A test category',
    )
    assert str(category) == category.name


def test_category_slug_generated_on_save(db):
    category = Category(
        name='Test Category',
        description='A test category',
    )
    category.save()
    assert category.slug == 'test-category'


def test_post_str():
    category = Category(
        name='Test Category',
        description='A test category',
    )
    post = Post(
        title='Test Post',
        content='This is a test post content.',
        category=category,
    )
    assert str(post) == post.title


def test_post_slug_generated_on_save(db, category_factory, author_factory):
    author = author_factory.create()
    category = category_factory.create()
    post = Post(
        title='Test Post',
        content='This is a test post content.',
        category=category,
        author=author,
    )
    post.save()
    assert post.slug == 'test-post'


def test_post_has_is_public_method(db, post_factory):
    post = post_factory.create(status='published')
    assert post.is_public() is True


def test_tag_str_():
    tag = Tag(name='Test Tag')
    assert str(tag) == tag.name


def test_tag_slug_generated_on_save(db, tag_factory):
    tag = Tag(name='Test Tag')
    tag.save()
    assert tag.slug == 'test-tag'
