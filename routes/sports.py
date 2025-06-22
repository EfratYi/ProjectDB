from flask import Blueprint, request, render_template, redirect
from db import get_connection

sports_bp = Blueprint('sports_bp', __name__, url_prefix='/sports')

@sports_bp.route("/")
def list_sports():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT sportid, sportname, category FROM sport ORDER BY sportid;
        """)

        rows = cur.fetchall()
        cur.close()
        conn.close()

        sports = [
            {"id": row[0], "name": row[1], "category": row[2]} for row in rows
        ]

        return render_template("sport/sports.html", sports=sports)

    except Exception as e:
        return f"שגיאה בשליפת ספורטים: {e}"


@sports_bp.route("/add", methods=["GET", "POST"])
def add_sport():
    if request.method == "POST":
        try:
            name = request.form["sportname"]
            category = request.form["category"]

            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO sport (sportname, category) VALUES (%s, %s)
            """, (name, category))
            conn.commit()
            cur.close()
            conn.close()

            return redirect("/sports")

        except Exception as e:
            # במקרה של שגיאה - טען את הטופס מחדש עם הודעת שגיאה
            return render_template("sport/add_sport.html", error=str(e),
                                   sportname=name,
                                   category=category)

    # GET - טען טופס ריק
    return render_template("sport/add_sport.html")


@sports_bp.route("/edit/<int:sport_id>", methods=["GET", "POST"])
def edit_sport(sport_id):
    if request.method == "POST":
        try:
            sportname = request.form["sportname"]
            category = request.form["category"]

            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE sport
                SET sportname = %s,
                    category = %s
                WHERE sportid = %s
            """, (sportname, category, sport_id))
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

            # שליפת הספורט עצמו
            cur.execute("SELECT sportid, sportname, category FROM sport WHERE sportid = %s", (sport_id,))
            sport = cur.fetchone()

            # שליפת רשימת קטגוריות ייחודיות מהטבלה עצמה
            cur.execute("SELECT DISTINCT category FROM sport WHERE category IS NOT NULL ORDER BY category")
            categories = [row[0] for row in cur.fetchall()]

            cur.close()
            conn.close()

            if sport:
                sport_dict = {
                    "sportid": sport[0],
                    "sportname": sport[1],
                    "category": sport[2]
                }
                return render_template("sport/edit_sport.html", sport=sport_dict, categories=categories)
            else:
                return "Sport not found"

        except Exception as e:
            return f"Error fetching sport: {e}"


def render_edit_sport_form(sport_id, error=None):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT sportname, category FROM sport WHERE sportid = %s", (sport_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            return "ספורט לא נמצא"

        sport = {
            "name": row[0],
            "category": row[1]
        }

        return render_template("sport/edit_sport.html", sport_id=sport_id, sport=sport, error=error)

    except Exception as e:
        return f"שגיאה בעריכת ספורט: {e}"


@sports_bp.route("/delete/<int:sport_id>", methods=["POST"])
def delete_sport(sport_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM sport WHERE sportid = %s", (sport_id,))
        conn.commit()
        cur.close()
        conn.close()

        return redirect("/sports")

    except Exception as e:
        return f"שגיאה במחיקת ספורט: {e}"
