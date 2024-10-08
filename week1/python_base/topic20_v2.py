from functools import wraps


USER_ROLE: str = "user"


class UserRoleManager:
    def __init__(self, role: str):
        self.role = role

    def __enter__(self):
        global USER_ROLE
        self._previous_role = USER_ROLE
        USER_ROLE = self.role

    def __exit__(self, exc_type, exc_val, exc_tb):
        global USER_ROLE
        USER_ROLE = self._previous_role


def access_control(roles: list[str]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if USER_ROLE in roles:
                return func(*args, **kwargs)
            else:
                raise PermissionError("Access denied for current user role!")

        return wrapper

    return decorator


@access_control(roles=["admin", "moderator"])
def get_important_data():
    return "Very important data"


with UserRoleManager(role="admin"):
    print(get_important_data())

with UserRoleManager(role="moderator"):
    print(get_important_data())

try:
    get_important_data()
except PermissionError as e:
    print(e)
