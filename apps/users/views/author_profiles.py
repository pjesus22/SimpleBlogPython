import json

from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

from apps.users.models import AuthorProfile, SocialAccount
from apps.users.serializers import AuthorProfileSerializer, SocialAccountSerializer
from apps.utils.decorators import admin_or_author_required, login_required
from apps.utils.jsonapi_responses import JsonApiResponseBuilder as jarb
from apps.utils.request_utils import extract_data_and_files
from apps.utils.validators import validate_invalid_fields, validate_required_fields


class AuthorProfileDetailView(View):
    http_method_names = ['get', 'patch', 'head', 'options']

    @method_decorator([login_required, admin_or_author_required])
    def patch(self, request, *args, **kwargs):
        try:
            data, files = extract_data_and_files(request)
            profile = get_object_or_404(AuthorProfile, user__id=kwargs.get('user_id'))

            if not (request.user.role == 'admin' or request.user.id == profile.user.id):
                return jarb.error(403, 'Forbidden', 'Permission denied')

            if data.get('bio'):
                profile.bio = data.get('bio')
            if files.get('profile_picture'):
                profile.profile_picture = files.get('profile_picture')

            profile.save()
            return jarb.ok(AuthorProfileSerializer.serialize_profile(profile))

        except (json.JSONDecodeError, ValueError, ValidationError) as e:
            return jarb.error(400, 'Bad Request', str(e))
        except Http404 as e:
            return jarb.error(404, 'Not Found', str(e))
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))


class SocialAccountListView(View):
    http_method_names = ['post']

    @method_decorator([login_required, admin_or_author_required])
    def post(self, request, *args, **kwargs):
        try:
            user = request.user
            profile = get_object_or_404(AuthorProfile, user__id=kwargs.get('user_id'))
            data = request.POST.dict()

            if not (user.role == 'admin' or user.id == profile.user.id):
                return jarb.error(403, 'Forbidden', 'Permission denied')

            allowed_fields = {'profile', 'provider', 'username', 'url'}
            required_fields = {'provider', 'username', 'url'}
            validate_invalid_fields(data, allowed_fields)
            validate_required_fields(data, required_fields)

            social = SocialAccount(
                profile=profile,
                provider=data['provider'],
                username=data['username'],
                url=data['url'],
            )

            social.save()

            return jarb.created(SocialAccountSerializer.serialize_social(social))
        except (ValueError, ValidationError, json.JSONDecodeError) as e:
            return jarb.error(400, 'Bad Request', str(e))
        except Http404 as e:
            return jarb.error(404, 'Not Found', str(e))
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))


class SocialAccountDetailView(View):
    http_method_names = ['patch', 'delete', 'head', 'options']

    @method_decorator([login_required, admin_or_author_required])
    def patch(self, request, *args, **kwargs):
        try:
            social = get_object_or_404(SocialAccount, id=kwargs.get('social_id'))
            user = request.user
            data = request.POST.dict()

            if not (user.role == 'admin' or user.id == social.profile.user.id):
                return jarb.error(403, 'Forbidden', 'Permission denied')

            allowed_fields = {'provider', 'username', 'url'}
            validate_invalid_fields(data, allowed_fields)

            for field in allowed_fields:
                if field in data:
                    setattr(social, field, data[field])

            social.save()
            return jarb.ok(SocialAccountSerializer.serialize_social(social))
        except (ValidationError, ValueError, json.JSONDecodeError) as e:
            return jarb.error(400, 'Bad Request', str(e))
        except Http404 as e:
            return jarb.error(404, 'Not Found', str(e))
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))

    @method_decorator([login_required, admin_or_author_required])
    def delete(self, request, *args, **kwargs):
        try:
            social = get_object_or_404(SocialAccount, id=kwargs.get('social_id'))
            user = request.user

            if not (user.role == 'admin' or user.id == social.profile.user.id):
                return jarb.error(403, 'Forbidden', 'Permission denied')

            social.delete()
            return jarb.no_content()
        except Http404 as e:
            return jarb.error(404, 'Not Found', str(e))
        except Exception as e:
            return jarb.error(500, 'Internal Server Error', str(e))
