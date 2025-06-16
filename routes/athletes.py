from flask import Blueprint, request, render_template, redirect, jsonify
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
            is_player = request.form.get("isplayer") == "on"
            height = request.form.get("athleteheight") or None

            team_id = int(request.form["teamid"]) if is_player else None
            jersey_number = request.form.get("athletejerseynum") if is_player else None
            position = request.form.get("athleteposition") if is_player else None

            conn = get_connection()
            cur = conn.cursor()

            # ✅ ולידציה אם מספר החולצה כבר תפוס
            if is_player and jersey_number is not None:
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM athlete 
                    WHERE teamid = %s AND athletejerseynum = %s
                """, (team_id, jersey_number))
                if cur.fetchone()[0] > 0:
                    cur.close()
                    conn.close()
                    return f"שגיאה: מספר חולצה {jersey_number} כבר תפוס בקבוצה זו."

            # 👇 ממשיכים להכין את הדאטה רק אחרי הוולידציה
            data = (
                request.form["athletename"],
                request.form["gender"],
                request.form["birthday"],
                int(request.form["countryid"]),
                team_id,
                is_player,
                height,
                jersey_number,
                position,
            )

            cur.execute("""
                INSERT INTO athlete (
                    athletename, gender, birthday, countryid,
                    teamid, isplayer, athleteheight,
                    athletejerseynum, athleteposition
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, data)
            conn.commit()
            cur.close()
            conn.close()
            return redirect("/athletes")

        except Exception as e:
            return f"שגיאה בהוספת אתלט: {e}"

    else:
        try:
            conn = get_connection()
            cur = conn.cursor()

            # שליפת המדינות
            cur.execute("SELECT countryid, countryname FROM country ORDER BY countryname")
            countries = cur.fetchall()

            # שליפת הקבוצות
            cur.execute("SELECT teamid, teamname FROM team ORDER BY teamname")
            teams = cur.fetchall()

            # שליפת תפקידים שונים אם רוצים
            cur.execute(
                "SELECT DISTINCT athleteposition FROM athlete WHERE athleteposition IS NOT NULL ORDER BY athleteposition")
            positions = [row[0] for row in cur.fetchall()]

            cur.close()
            conn.close()

            return render_template("athletes/add_athlete.html", countries=countries, teams=teams, positions=positions)

        except Exception as e:
            return f"שגיאה בטעינת טופס הוספה: {e}"

@athletes_bp.route("/taken_numbers/<int:team_id>")
def taken_jersey_numbers(team_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT athletejerseynum 
            FROM athlete 
            WHERE teamid = %s AND athletejerseynum IS NOT NULL
        """, (team_id,))
        numbers = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return jsonify(numbers)
    except Exception as e:
        return jsonify([]), 500


@athletes_bp.route("/edit/<int:athlete_id>", methods=["GET", "POST"])
def edit_athlete(athlete_id):
    if request.method == "POST":
        try:
            is_player = request.form.get("isplayer") == "on"

            height_input = request.form.get("athleteheight")
            height = height_input if height_input != "" else None

            # שליפה של שדות רלוונטיים רק אם הוא שחקן
            team_id = int(request.form["teamid"]) if is_player else None
            jersey_number = request.form.get("athletejerseynum") if is_player else None
            position = request.form.get("athleteposition") if is_player else None

            conn = get_connection()
            cur = conn.cursor()
            if is_player and jersey_number is not None:
                cur.execute("""
                               SELECT COUNT(*) 
                               FROM athlete 
                               WHERE teamid = %s AND athletejerseynum = %s
                           """, (team_id, jersey_number))
                if cur.fetchone()[0] > 0:
                    cur.close()
                    conn.close()
                    return f"שגיאה: מספר חולצה {jersey_number} כבר תפוס בקבוצה זו."

            data = (
                request.form["athletename"],
                request.form["gender"],
                request.form["birthday"],
                int(request.form["countryid"]),
                team_id,
                is_player,
                height,
                jersey_number,
                position,
                athlete_id
            )


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
            return f"שגיאה בעדכון אתלט: {e}"

    else:
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("SELECT countryid, countryname FROM country ORDER BY countryname")
            countries = cur.fetchall()

            cur.execute("SELECT teamid, teamname FROM team ORDER BY teamname")
            teams = cur.fetchall()

            cur.execute(
                "SELECT DISTINCT athleteposition FROM athlete WHERE athleteposition IS NOT NULL ORDER BY athleteposition")
            positions = [row[0] for row in cur.fetchall()]

            cur.execute("""
                SELECT 
                    athleteid, athletename, gender, birthday,
                    countryid, teamid, isplayer,
                    athleteheight, athletejerseynum, athleteposition
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
                    "birthday": athlete[3].strftime("%Y-%m-%d"),
                    "countryid": athlete[4],
                    "teamid": athlete[5],
                    "is_player": athlete[6],
                    "height": athlete[7],
                    "jersey_number": athlete[8],
                    "position": athlete[9],
                }
                return render_template("athletes/edit_athlete.html", athlete=athlete_dict, countries=countries, teams=teams, positions=positions)
            else:
                return "לא נמצא אתלט"

        except Exception as e:
            return f"שגיאה בטעינת נתוני אתלט: {e}"



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
