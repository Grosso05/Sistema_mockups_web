from functools import wraps
from flask import redirect, url_for, abort
from flask_login import current_user

def roles_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('routes.login'))
            if current_user.user_rol not in roles:
                return abort(403)  # Prohibido: el usuario no tiene los roles necesarios
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper