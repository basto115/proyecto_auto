from rest_framework.response import Response
from rest_framework import status
from functools import wraps

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            if not request.user.is_authenticated:
                return Response({'error': 'No autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
            if request.user.rol not in allowed_roles:
                return Response({'error': 'No tienes permiso'}, status=status.HTTP_403_FORBIDDEN)
            return view_func(self, request, *args, **kwargs)
        return _wrapped_view
    return decorator