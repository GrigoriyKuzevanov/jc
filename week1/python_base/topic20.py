from functools import wraps


class User:
    def __init__(self, role: str):
        self.role = role


def access_control(roles: list[str]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_user: User = kwargs.get("current_user")
            if current_user and current_user.role in roles:
                return func(*args, **kwargs)
            else:
                raise PermissionError("Access denied for current user's role")

        return wrapper

    return decorator


@access_control(roles=["admin", "moderator"])
def get_data(*, current_user: User = None):
    return {"detail": "Very important data"}


some_user_1 = User("admin")
some_user_2 = User("moderator")
some_user_3 = User("user")

print(get_data(current_user=some_user_1))
print(get_data(current_user=some_user_2))
print(get_data(current_user=some_user_3))
