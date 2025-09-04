import pytest


def build_expected_error(
    detail: str, status: int = 400, title: str = None, meta: dict = None
):
    titles = {
        400: 'Bad Request',
        404: 'Not Found',
        500: 'Internal Server Error',
        403: 'Forbidden',
        401: 'Unauthorized',
    }
    return {
        'status': str(status),
        'title': title or titles.get(status, 'Error'),
        'detail': detail,
        'meta': meta or {},
    }


@pytest.fixture
def fake_method_factory():
    def _fake_method(return_value=None, raise_exception: Exception = None):
        def _method(*args, **kwargs):
            if raise_exception:
                raise raise_exception
            return return_value

        return _method

    return _fake_method
