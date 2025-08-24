from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List, Optional, Union

from django.http import HttpResponse, JsonResponse


@dataclass
class JsonApiError:
    status: str
    title: str
    detail: str
    meta: Optional[Dict] = None


class JsonApiResponseBuilder:
    @staticmethod
    def _build_response(
        data: Optional[Union[Dict, List]] = None,
        errors: Optional[List[JsonApiError]] = None,
        links: Optional[Dict] = None,
    ) -> Dict:
        payload = {}
        if data is not None:
            payload['data'] = data
        if errors:
            payload['errors'] = [asdict(error) for error in errors]
        if links:
            payload['links'] = links
        return payload

    @staticmethod
    def ok(data: Dict, meta: Optional[Dict] = None) -> JsonResponse:
        response_data = JsonApiResponseBuilder._build_response(data=data)
        response_data['meta'] = meta or {'timestamp': datetime.now().isoformat()}
        return JsonResponse(response_data, status=200)

    @staticmethod
    def created(data: Dict, meta: Optional[Dict] = None) -> JsonResponse:
        response_data = JsonApiResponseBuilder._build_response(data=data)
        response_data['meta'] = meta or {'timestamp': datetime.now().isoformat()}
        return JsonResponse(response_data, status=201)

    @staticmethod
    def no_content(**kwargs: Dict) -> HttpResponse:
        return HttpResponse(status=204, **kwargs)

    @staticmethod
    def error(
        status_code: int,
        title: str,
        detail: str,
        meta: Optional[Dict] = None,
        **kwargs: Dict,
    ) -> JsonResponse:
        error = JsonApiError(
            status=str(status_code),
            title=title,
            detail=detail,
            meta=meta or {'timestamp': datetime.now().isoformat()},
        )
        payload = JsonApiResponseBuilder._build_response(errors=[error])
        return JsonResponse(payload, status=status_code, **kwargs)

    @staticmethod
    def validation_errors_from_dict(
        error_dict: Dict[str, List[str]],
        status_code: int = 400,
        title: str = 'Bad Request',
        meta: Optional[Dict] = None,
    ):
        errors = []
        for field, messages in error_dict.items():
            for message in messages:
                error_context = {
                    **({'field': field} if field != '__all__' else {}),
                    'timestamp': datetime.now().isoformat(),
                    **(meta or {}),
                }

                errors.append(
                    JsonApiError(
                        status=str(status_code),
                        title=title,
                        detail=message,
                        meta=error_context if error_context else None,
                    )
                )
        payload = JsonApiResponseBuilder._build_response(errors=errors)
        return JsonResponse(payload, status=status_code)

    @staticmethod
    def validation_errors_from_list(
        error_list: List[str],
        status_code: int = 400,
        title: str = 'Bad Request',
        meta: Optional[Dict] = None,
    ):
        errors = []
        for message in error_list:
            errors.append(
                JsonApiError(
                    status=str(status_code),
                    title=title,
                    detail=message,
                    meta=meta or {'timestamp': datetime.now().isoformat()},
                )
            )
        payload = JsonApiResponseBuilder._build_response(errors=errors)
        return JsonResponse(payload, status=status_code)
