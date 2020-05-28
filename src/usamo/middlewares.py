from django.http import JsonResponse
from rest_framework import status
from django.conf import settings


class FilesSizeValidatorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        for filename in request.FILES:
            if request.FILES[filename].size > int(settings.MAX_UPLOAD_MB_SIZE) * 1024 * 1024:
                error_message = f'Rozmiar pliku powinien być nie większy niż {settings.MAX_UPLOAD_MB_SIZE} MB'
                return self.__get_error_json_response(error_message)
        return self.get_response(request)

    @staticmethod
    def __get_error_json_response(message):
        return JsonResponse({'error': message}, status=status.HTTP_400_BAD_REQUEST)
