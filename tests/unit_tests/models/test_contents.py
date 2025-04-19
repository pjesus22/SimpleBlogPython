import pytest

pytestmark = pytest.mark.django_db


@pytest.fixture
def category_inst(category_factory):
    return category_factory.create(name='Test Category')


@pytest.fixture
def post_inst(post_factory):
    return post_factory.create(title='Test Post')


@pytest.fixture
def tag_inst(tag_factory):
    return tag_factory.create(name='Test Tag')


def test_category_str_(category_inst):
    assert category_inst.__str__() == category_inst.name


def test_category_slug_generated_on_save(category_inst):
    assert category_inst.slug == 'test-category'


def test_post_str_(post_inst):
    assert post_inst.__str__() == post_inst.title


def test_post_slug_generated_on_save(post_inst):
    assert post_inst.slug == 'test-post'


def test_tag_str_(tag_inst):
    assert tag_inst.__str__() == tag_inst.name


def test_tag_slug_generated_on_save(tag_inst):
    assert tag_inst.slug == 'test-tag'
