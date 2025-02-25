from django.shortcuts import redirect
from django.http import HttpResponse

def role_required(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            user_role = request.session.get('user_role')  # Get role from session

            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('unauthorized_access')
            
        return wrapper_func
    return decorator
