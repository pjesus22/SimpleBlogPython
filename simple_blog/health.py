import datetime
import logging
import os
import time

from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)

START_TIME = time.time()


def check_database():
    """
    Returns a dict with database health info
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        return {'status': 'ok'}
    except Exception as e:
        logger.error(f'Health check database error: {e}')
        return {'status': 'error', 'message': str(e)}


@never_cache
@require_GET
def health_check(request):
    """
    Health check endpoint.
    """
    health_data = {
        'status': 'ok',
        'timestamp': datetime.datetime.now().isoformat(),
        'version': '0.1.0',
        'uptime_seconds': int(time.time() - START_TIME),
    }

    # Database
    db_status = check_database()
    health_data['database'] = db_status
    if db_status['status'] != 'ok':
        health_data['status'] = 'error'

    # Enviroment
    health_data['environment'] = (
        'local'
        if os.environ.get('DJANGO_SETTINGS_MODULE').endswith('local')
        else 'production'
    )

    # Metrics
    health_data['metrics'] = {
        'python_version': os.getenv('PYTHONVERSION', '3.x'),
        'debug_mode': settings.DEBUG,
    }

    status_code = 200 if health_data['status'] == 'ok' else 503
    response_data = {'data': health_data}

    return JsonResponse(response_data, status=status_code)
