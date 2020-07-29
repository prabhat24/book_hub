from django.http import JsonResponse


def authenticate_roles(allowed_roles=[]):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.groups.exists():
                user_group_list = [group.name for group in request.user.groups.all()]
                for role in user_group_list:
                    if role in allowed_roles:
                        return view_func(request, *args, **kwargs)
                return JsonResponse({'res': f"user should belong to {allowed_roles}"})

        return wrapper

    return decorator
