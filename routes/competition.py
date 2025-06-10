from flask import Blueprint, request, render_template, redirect
from db import get_connection

competitions_bp = Blueprint('competitions', __name__, url_prefix='/competitions')

@competitions_bp.route("/")
def competitions():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT c.id, c.name, c.date, s.name AS sport_name
            FROM competitions c
            JOIN sports s ON c.sport_id = s.id
            ORDER BY c.id
        """)
        data = cur.fetchall()
        cur.close()
        conn.close()

        competitions = [
            {"id": row[0], "name": row[1], "date": row[2], "sport": row[3]}
            for row in data
        ]
        return render_template("competitions/competitions.html", competitions=competitions)
    except Exception as e:
        return f"Error fetching competitions: {e}"

@competitions_bp.route("/add", methods=["GET", "POST"])
def add_competition():
    if request.method == "POST":
        name = request.form["name"]
        date = request.form["date"]
        sport_id = request.form["sport_id"]

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO competitions (name, date, sport_id) VALUES (%s, %s, %s)
            """, (name, date, sport_id))
            conn.commit()
            cur.close()
            conn.close()
            return redirect("/competitions")
        except Exception as e:
            return f"Error adding competition: {e}"
    else:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM sports ORDER BY name")
            sports = cur.fetchall()
            cur.close()
            conn.close()
            return render_template("competitions/add_competition.html", sports=sports)
        except Exception as e:
            return f"Error fetching sports list: {e}"

@competitions_bp.route("/edit/<int:competition_id>", methods=["GET", "POST"])
def edit_competition(competition_id):
    if request.method == "POST":
        name = request.form["name"]
        date = request.form["date"]
        sport_id = request.form["sport_id"]
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE competitions SET name = %s, date = %s, sport_id = %s WHERE id = %s
            """, (name, date, sport_id, competition_id))
            conn.commit()
            cur.close()
            conn.close()
            return redirect("/competitions")
        except Exception as e:
            return f"Error updating competition: {e}"
    else:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, name, date, sport_id FROM competitions WHERE id = %s", (competition_id,))
            competition = cur.fetchone()
            cur.execute("SELECT id, name FROM sports ORDER BY name")
            sports = cur.fetchall()
            cur.close()
            conn.close()

            if competition:
                comp_dict = {
                    "id": competition[0],
                    "name": competition[1],
                    "date": competition[2],
                    "sport_id": competition[3]
                }
                return render_template("competitions/edit_competition.html", competition=comp_dict, sports=sports)
            else:
                return "Competition not found"
        except Exception as e:
            return f"Error fetching competition: {e}"

@competitions_bp.route("/delete/<int:competition_id>", methods=["POST"])
def delete_competition(competition_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM competitions WHERE id = %s", (competition_id,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/competitions")
    except Exception as e:
        return f"Error deleting competition: {e}"
