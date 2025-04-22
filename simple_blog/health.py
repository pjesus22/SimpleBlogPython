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

# Track application start time for uptime calculation
START_TIME = time.time()


@never_cache
@require_GET
def health_check(request):
    """
    Health check endpoint for monitoring and orchestration systems.

    Checks:
    - Database connection
    - Application uptime
    - Basic system info

    Returns a JSON response with health status and metrics.
    """
    health_data = {
        'status': 'ok',
        'timestamp': datetime.datetime.now().isoformat(),
        'version': '0.1.0',
        'uptime_seconds': int(time.time() - START_TIME),
    }

    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        health_data['database'] = {'status': 'ok'}
    except Exception as e:
        health_data['status'] = 'error'
        health_data['database'] = {'status': 'error', 'message': str(e)}
        logger.error(f'Health check database error: {e}')

    # Check environment
    health_data['environment'] = (
        settings.ENVIRONMENT if hasattr(settings, 'ENVIRONMENT') else 'unknown'
    )

    # Include additional system metrics
    health_data['metrics'] = {
        'python_version': os.getenv('PYTHONVERSION', '3.x'),
        'debug_mode': settings.DEBUG,
    }

    # Return status code based on overall health
    status_code = 200 if health_data['status'] == 'ok' else 503

    # Format according to the API standard
    response_data = {'data': health_data}

    return JsonResponse(response_data, status=status_code)
