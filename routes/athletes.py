from flask import Blueprint, request, render_template, redirect
from db import get_connection

athletes_bp = Blueprint("athletes_bp", __name__, url_prefix="/athletes")


@athletes_bp.route("/")
def list_athletes():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
    SELECT 
    a.athleteid,
    a.athletename,
    a.gender,
    a.birthday,
    c.countryname,
    t.teamname,
    a.isplayer,
    a.athleteheight,
    a.athletejerseynum,
    a.athleteposition
FROM athlete a
LEFT JOIN country c ON a.countryid = c.countryid
LEFT JOIN team t ON a.teamid = t.teamid
ORDER BY a.athleteid
""")

        rows = cur.fetchall()
        cur.close()
        conn.close()

        athletes = [
            {
                "id": row[0],
                "name": row[1],
                "gender": row[2],
                "birthday": row[3],
                "country_name": row[4],
                "team_name": row[5],
                "is_player": row[6],
                "height": row[7],
                "jersey_number": row[8],
                "position": row[9],
            }
            for row in rows
        ]
        return render_template("athletes/athletes.html", athletes=athletes)

    except Exception as e:
        return f"Error fetching athletes: {e}"


@athletes_bp.route("/add", methods=["GET", "POST"])
def add_athlete():
    if request.method == "POST":
        try:
            data = (
                request.form["athletename"],
                request.form["gender"],
                request.form["birthday"],
                request.form["countryid"],
                request.form["teamid"],
                request.form.get("isplayer") == "on",
                request.form["athleteheight"],
                request.form["athletejerseynum"],
                request.form["athleteposition"],
            )

            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO athlete (athletename, gender, birthday, countryid, teamid,
                                     isplayer, athleteheight, athletejerseynum, athleteposition)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, data)
            conn.commit()
            cur.close()
            conn.close()
            return redirect("/athletes")

        except Exception as e:
            return f"Error adding athlete: {e}"
    else:
        return render_template("athletes/add_athlete.html")


@athletes_bp.route("/edit_athlete/<int:athlete_id>", methods=["GET", "POST"])
def edit_athlete(athlete_id):
    if request.method == "POST":
        try:
            data = (
                request.form["athletename"],
                request.form["gender"],
                request.form["birthday"],
                request.form["countryid"],
                request.form["teamid"],
                request.form.get("isplayer") == "on",
                request.form["athleteheight"],
                request.form["athletejerseynum"],
                request.form["athleteposition"],
                athlete_id
            )

            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE athlete SET
                    athletename = %s,
                    gender = %s,
                    birthday = %s,
                    countryid = %s,
                    teamid = %s,
                    isplayer = %s,
                    athleteheight = %s,
                    athletejerseynum = %s,
                    athleteposition = %s
                WHERE athleteid = %s
            """, data)
            conn.commit()
            cur.close()
            conn.close()
            return redirect("/athletes")

        except Exception as e:
            return f"Error updating athlete: {e}"

    else:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT athleteid, athletename, gender, birthday, countryid, teamid,
                       isplayer, athleteheight, athletejerseynum, athleteposition
                FROM athlete
                WHERE athleteid = %s
            """, (athlete_id,))
            athlete = cur.fetchone()
            cur.close()
            conn.close()

            if athlete:
                athlete_dict = {
                    "id": athlete[0],
                    "name": athlete[1],
                    "gender": athlete[2],
                    "birthday": athlete[3],
                    "country_id": athlete[4],
                    "team_id": athlete[5],
                    "is_player": athlete[6],
                    "height": athlete[7],
                    "jersey_number": athlete[8],
                    "position": athlete[9],
                }
                return render_template("athletes/edit_athlete.html", athlete=athlete_dict)
            else:
                return "Athlete not found"

        except Exception as e:
            return f"Error fetching athlete: {e}"


@athletes_bp.route("/delete/<int:athlete_id>", methods=["POST"])
def delete_athlete(athlete_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM athlete WHERE athleteid = %s", (athlete_id,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect("/athletes")
    except Exception as e:
        return f"Error deleting athlete: {e}"
