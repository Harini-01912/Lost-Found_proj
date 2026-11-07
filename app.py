import os
from datetime import date

from flask import Flask, abort, flash, redirect, render_template, request, url_for

from database import init_db, get_db, close_db
from matching import MATCH_THRESHOLD, find_matches, match_score


CATEGORIES = ("Electronics", "Accessories", "Documents", "Bags", "Other")
ITEM_FIELDS = ("name", "category", "description", "location", "event_date", "contact")

app = Flask(__name__, instance_relative_config=True)
app.config.update(
    DATABASE=os.path.join(app.instance_path, "lost_found.db"),
    SECRET_KEY=os.environ.get("SECRET_KEY", "local-development-key"),
)
os.makedirs(app.instance_path, exist_ok=True)
app.teardown_appcontext(close_db)
init_db(app)


def valid_kind(kind):
    return kind in ("lost", "found")


def load_item(kind, item_id):
    if not valid_kind(kind):
        abort(404)
    item = get_db().execute(
        "SELECT * FROM items WHERE id = ? AND kind = ?", (item_id, kind)
    ).fetchone()
    if item is None:
        abort(404)
    return item


def render_item_form(kind, errors=None, values=None, status=200):
    return (
        render_template(
            "item_form.html",
            kind=kind,
            categories=CATEGORIES,
            today=date.today().isoformat(),
            errors=errors or [],
            values=values or {},
        ),
        status,
    )


@app.route("/")
def home():
    db = get_db()
    recent_lost = db.execute(
        "SELECT * FROM items WHERE kind = 'lost' ORDER BY created_at DESC, id DESC LIMIT 5"
    ).fetchall()
    recent_found = db.execute(
        "SELECT * FROM items WHERE kind = 'found' ORDER BY created_at DESC, id DESC LIMIT 5"
    ).fetchall()
    return render_template(
        "index.html", recent_lost=recent_lost, recent_found=recent_found
    )


@app.route("/report/<kind>", methods=("GET", "POST"))
def report_item(kind):
    if not valid_kind(kind):
        abort(404)

    if request.method == "GET":
        return render_item_form(kind)

    values = {field: request.form.get(field, "").strip() for field in ITEM_FIELDS}
    errors = []
    for field in ITEM_FIELDS:
        if not values[field]:
            errors.append(f"{field.replace('_', ' ').capitalize()} is required.")

    if values["category"] not in CATEGORIES:
        errors.append("Choose a valid item category.")
    if values["event_date"]:
        try:
            event_date = date.fromisoformat(values["event_date"])
            if event_date > date.today():
                errors.append("The item date cannot be in the future.")
        except ValueError:
            errors.append("Enter a valid date.")

    length_limits = {
        "name": 120,
        "description": 2000,
        "location": 200,
        "contact": 200,
    }
    for field, limit in length_limits.items():
        if len(values[field]) > limit:
            errors.append(f"{field.capitalize()} must be {limit} characters or fewer.")

    if errors:
        return render_item_form(kind, errors, values, 400)

    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO items (kind, name, category, description, location, event_date, contact)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            kind,
            values["name"],
            values["category"],
            values["description"],
            values["location"],
            values["event_date"],
            values["contact"],
        ),
    )
    db.commit()
    item_id = cursor.lastrowid
    flash(
        f"Your {kind} item report has been saved. Here are possible matches.",
        "success",
    )
    return redirect(url_for("item_matches", kind=kind, item_id=item_id))


@app.route("/items/<kind>/<int:item_id>")
def item_detail(kind, item_id):
    item = load_item(kind, item_id)
    return render_template("item_detail.html", item=item)


@app.route("/matches/<kind>/<int:item_id>")
def item_matches(kind, item_id):
    item = load_item(kind, item_id)
    matches = find_matches(item, "found" if kind == "lost" else "lost")
    return render_template(
        "matches.html",
        item=item,
        matches=matches,
        threshold=MATCH_THRESHOLD,
    )


@app.route("/dashboard")
def dashboard():
    db = get_db()
    lost_items = db.execute(
        "SELECT * FROM items WHERE kind = 'lost' ORDER BY created_at DESC, id DESC"
    ).fetchall()
    found_items = db.execute(
        "SELECT * FROM items WHERE kind = 'found' ORDER BY created_at DESC, id DESC"
    ).fetchall()
    potential_matches = []
    for lost_item in lost_items:
        for found_item in found_items:
            score = match_score(lost_item, found_item)
            if score >= MATCH_THRESHOLD:
                potential_matches.append(
                    {"lost": lost_item, "found": found_item, "score": score}
                )
    potential_matches.sort(key=lambda result: result["score"], reverse=True)
    return render_template(
        "dashboard.html",
        lost_items=lost_items,
        found_items=found_items,
        potential_matches=potential_matches,
        threshold=MATCH_THRESHOLD,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)