from flask import Blueprint, current_app

bp = Blueprint("main", __name__)

@bp.route("/")
def root():
    return current_app.send_static_file("index.html")

@bp.app_errorhandler(404)
def not_found(_):
    return current_app.send_static_file("index.html")
