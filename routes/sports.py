from flask import Blueprint, request, render_template, redirect
from db import get_connection

sports_bp = Blueprint('sports', __name__, url_prefix='/sports')

@sports_bp.route("/")
def sports():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM sports ORDER BY id")
        sports_data = cur.fetchall()
        cur.close()
        conn.close()

        sports = [{"id": row[0], "name": row[1]} for row in sports_data]
        return render_template("sports/sports.html", sports=sports)
    except Exception as e:
        return f"Error fetching sports: {e}"

@sports_bp.route("/add", methods=["GET", "POST"])
def add_sport():
    if request.method == "POST":
        name = request.form["name"]

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO sports (name) VALUES (%s)", (name,))
            conn.commit()
            cur.close()
            conn.close()
            return redirect("/sports")
        except Exception as e:
            return f"Error adding sport: {e}"
    return render_template("sports/add_sport.html")

@sports_bp.route("/edit/<int:sport_id>", methods=["GET", "POST"])
def edit_sport(sport_id):
    if request.method == "POST":
        name = request.form["name"]
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE sports SET name = %s WHERE id = %s", (name, sport_id))
            conn.commit()
            cur.close()
            conn.close()
            return redirect("/sports")
        except Exception as e:
            return f"Error updating sport: {e}"
    else:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM sports WHERE id = %s", (sport_id,))
            sport = cur.fetchone()
            cur.close()
            conn.close()
            if sport:
                return render_template("sports/edit_sport.html", sport={"id": sport[0], "name": sport[1]})
            else:
                return "Sport not found"
        except Exception as e:
            return f"Error fetching sport: {e}"

@sports_bp.route("/delete/<int:sport_id>", methods=["POST"])
def delete_sport(sport_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM sports WHERE id = %s", (sport_id,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/sports")
    except Exception as e:
        return f"Error deleting sport: {e}"
