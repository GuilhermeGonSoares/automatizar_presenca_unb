from flask import Blueprint, render_template

bp_name = "hello"
bp = Blueprint(bp_name, __name__)


@bp.route("/")
def hello():
    return render_template("index.html")
