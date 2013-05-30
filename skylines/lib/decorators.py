from functools import wraps

from formencode import Invalid

from flask import current_app, request, flash, redirect, url_for
from flask.ext.login import current_user


def jsonp(func):
    """Wraps JSONified output for JSONP requests."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = request.args.get('callback', False)
        if callback:
            data = str(func(*args, **kwargs).data)
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function


class validate:
    def __init__(self, form, errorhandler):
        self.form = form
        self.errorhandler = errorhandler

    def __call__(self, fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            try:
                self.form.validate(request.form)
            except Invalid:
                return self.errorhandler()
            else:
                return fn(*args, **kwargs)

        return decorated_view


class login_required:
    def __init__(self, msg=None):
        self.msg = msg

    def __call__(self, fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated():
                if self.msg:
                    flash(self.msg)

                return redirect(url_for('login', next=request.url))

            return fn(*args, **kwargs)
        return decorated_view
