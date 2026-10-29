from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import text

from .models import Message, db

bp = Blueprint("main", __name__)


@bp.get("/")
def index():
    messages = Message.query.order_by(Message.created_at.desc()).all()
    return render_template("index.html", messages=messages)


@bp.post("/")
def add_message():
    name = request.form.get("name", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not message:
        current_app.logger.warning("Rejected empty form submission")
        flash("Name and message are both required.")
        return redirect(url_for("main.index"))

    db.session.add(Message(name=name[:100], message=message))
    db.session.commit()
    current_app.logger.info("New message saved from %s", name)

    # Redirect after POST so a page refresh doesn't resubmit the form
    return redirect(url_for("main.index"))


@bp.get("/health")
def health():
    db.session.execute(text("SELECT 1"))
    return {"status": "ok"}
