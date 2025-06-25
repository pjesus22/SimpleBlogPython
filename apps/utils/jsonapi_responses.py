from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List, Optional, Union

from django.http import HttpResponse, JsonResponse


@dataclass
class JsonApiError:
    status: str
    title: str
    detail: str


@dataclass
class JsonApiResponseBuilder:
    @staticmethod
    def _build_response(
        data: Optional[Union[Dict, List]] = None,
        errors: Optional[List[JsonApiError]] = None,
        meta: Optional[Dict] = None,
        links: Optional[Dict] = None,
    ) -> Dict:
        payload = {}
        if data is not None:
            payload['data'] = data
        if errors:
            payload['errors'] = [asdict(error) for error in errors]
        if meta:
            payload['meta'] = meta
        if links:
            payload['links'] = links

        return payload

    @staticmethod
    def ok(
        data: Dict,
        meta: Optional[Dict] = None,
    ) -> JsonResponse:
        response_data = JsonApiResponseBuilder._build_response(
            data=data, meta=meta or {'timestamp': datetime.now().isoformat()}
        )
        return JsonResponse(response_data, status=200)

    @staticmethod
    def created(
        data: Dict,
        meta: Optional[Dict] = None,
    ) -> JsonResponse:
        response_data = JsonApiResponseBuilder._build_response(data=data, meta=meta)
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
        )
        payload = JsonApiResponseBuilder._build_response(
            errors=[error], meta=meta or {'timestamp': datetime.now().isoformat()}
        )
        return JsonResponse(payload, status=status_code, **kwargs)
