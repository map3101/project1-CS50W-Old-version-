from flask import redirect, render_template, request, session, flash, url_for
from functools import wraps

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get("user_id") is None:
            flash("You need to login")
            return redirect(url_for('login'))
        
        else:
            return f(*args, **kwargs)
    
    return wrap