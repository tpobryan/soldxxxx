import re
import random
from flask import Blueprint, render_template, request, jsonify

main_bp = Blueprint("main", __name__)

# Matches: "Name - HH:MM:SS sold N" or "Name - +HH:MM:SS sold N"
SOLD_PATTERN = re.compile(r"(.+?) - \+?\d+:\d{2}:\d{2} sold (\d+)")


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/process", methods=["POST"])
def process():
    text = request.form.get("text", "")
    sort_option = request.form.get("sort_option", "unsorted")
    unique_only = request.form.get("unique_only", "true") == "true"

    try:
        target_number = int(request.form.get("number", ""))
    except ValueError:
        return jsonify({"error": "Please enter a valid sold number."}), 400

    names = []
    for line in text.splitlines():
        match = SOLD_PATTERN.search(line)
        if match:
            name, sold_str = match.groups()
            if int(sold_str) == target_number:
                names.append(name.strip())

    if unique_only:
        names = list(dict.fromkeys(names))

    if sort_option == "random":
        random.shuffle(names)
    elif sort_option == "alphabetical":
        names.sort()

    return jsonify({"names": names, "count": len(names)})
