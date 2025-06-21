from flask import Blueprint, request, render_template, redirect
from db import get_connection

competitions_bp = Blueprint('competitions_bp', __name__, url_prefix='/competitions')


@competitions_bp.route("/")
def list_competitions():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                c.competitionid,
                c.competitionname,
                c.compdate,
                c.competitiontype,
                s.sportname AS sport_name,
                r.reffirstname || ' ' || r.reflastname AS referee_name,
                c.tournamentid,
                v.venuename AS venue_name
            FROM competition c
            LEFT JOIN sport s ON c.sportid = s.sportid
            LEFT JOIN referee r ON c.refereeid = r.refereeid
            LEFT JOIN venue v ON c.venueid = v.venueid
            ORDER BY c.competitionid;
        """)

        rows = cur.fetchall()
        cur.close()
        conn.close()

        competitions = [
            {
                "id": row[0],
                "name": row[1],
                "date": row[2],
                "type": row[3],
                "sport": row[4],
                "referee": row[5],
                "tournament": row[6],
                "venue": row[7]
            }
            for row in rows
        ]
        return render_template("competition/competitions.html", competitions=competitions)

    except Exception as e:
        return f"שגיאה בשליפת תחרויות: {e}"


@competitions_bp.route("/add", methods=["GET", "POST"])
def add_competition():
    if request.method == "POST":
        try:
            competitionname = request.form["competitionname"]
            compdate = request.form["compdate"]
            competitiontype = request.form["competitiontype"]
            sportid = int(request.form["sportid"])
            refereeid = request.form.get("refereeid") or None
            venueid = request.form.get("venueid") or None
            tournamentid = request.form.get("tournamentid") or None

            if refereeid: refereeid = int(refereeid)
            if venueid: venueid = int(venueid)
            if tournamentid: tournamentid = int(tournamentid)

            # 🕵️‍♀️ Validate competition date vs tournament year
            from datetime import datetime
            comp_year = datetime.strptime(compdate, "%Y-%m-%d").year

            if tournamentid:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("SELECT tournamentyear FROM tournament WHERE tournamentid = %s", (tournamentid,))
                result = cur.fetchone()
                if result:
                    tournament_year = result[0]
                    if comp_year > tournament_year:
                        # ❌ Date too late
                        raise ValueError(f"תאריך התחרות ({comp_year}) מאוחר משנה של הטורניר ({tournament_year})")
                cur.close()
                conn.close()

            # ✅ Passed validation - insert
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO competition (
                    competitionname, compdate, competitiontype, sportid,
                    refereeid, venueid, tournamentid
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (competitionname, compdate, competitiontype, sportid,
                  refereeid, venueid, tournamentid))
            conn.commit()
            cur.close()
            conn.close()

            return redirect("/competitions")

        except Exception as e:
            # 👇 Reload form with error message
            try:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("SELECT sportid, sportname FROM sport ")
                sports = cur.fetchall()
                cur.execute("SELECT refereeid, reffirstname, reflastname FROM referee ORDER BY reffirstname")
                referees = cur.fetchall()
                cur.execute("SELECT venueid, venuename FROM venue ORDER BY venuename")
                venues = cur.fetchall()
                cur.execute("SELECT tournamentid, tournamentyear, hostcountry FROM tournament ORDER BY tournamentyear DESC")
                tournaments = cur.fetchall()
                cur.close()
                conn.close()

                return render_template("competition/add_competition.html",
                                       sports=sports,
                                       referees=referees,
                                       venues=venues,
                                       tournaments=tournaments,
                                       error=str(e))
            except:
                return f"שגיאה נוספת בעת טעינת הטופס: {e}"

    else:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT sportid, sportname FROM sport ")
            sports = cur.fetchall()
            cur.execute("SELECT refereeid, reffirstname, reflastname FROM referee ORDER BY reffirstname")
            referees = cur.fetchall()
            cur.execute("SELECT venueid, venuename FROM venue ORDER BY venuename")
            venues = cur.fetchall()
            cur.execute("SELECT tournamentid, tournamentyear, hostcountry FROM tournament ORDER BY tournamentyear DESC")
            tournaments = cur.fetchall()
            cur.close()
            conn.close()

            return render_template("competition/add_competition.html",
                                   sports=sports,
                                   referees=referees,
                                   venues=venues,
                                   tournaments=tournaments)
        except Exception as e:
            return f"שגיאה בטעינת טופס הוספת תחרות: {e}"


@competitions_bp.route("/edit/<int:competition_id>", methods=["GET", "POST"])
def edit_competition(competition_id):
    if request.method == "POST":
        try:
            competitionname = request.form["competitionname"]
            compdate = request.form["compdate"]
            competitiontype = request.form["competitiontype"]
            sportid = int(request.form["sportid"])
            refereeid = request.form.get("refereeid") or None
            venueid = request.form.get("venueid") or None
            tournamentid = request.form.get("tournamentid") or None

            if refereeid: refereeid = int(refereeid)
            if venueid: venueid = int(venueid)
            if tournamentid: tournamentid = int(tournamentid)

            from datetime import datetime
            comp_year = datetime.strptime(compdate, "%Y-%m-%d").year

            if tournamentid:
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("SELECT tournamentyear FROM tournament WHERE tournamentid = %s", (tournamentid,))
                result = cur.fetchone()
                if result:
                    tournament_year = result[0]
                    if comp_year > tournament_year:
                        raise ValueError(f"תאריך התחרות ({comp_year}) מאוחר משנה של הטורניר ({tournament_year})")
                cur.close()
                conn.close()

            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE competition SET
                    competitionname = %s,
                    compdate = %s,
                    competitiontype = %s,
                    sportid = %s,
                    refereeid = %s,
                    venueid = %s,
                    tournamentid = %s
                WHERE competitionid = %s
            """, (competitionname, compdate, competitiontype, sportid, refereeid, venueid, tournamentid, competition_id))
            conn.commit()
            cur.close()
            conn.close()

            return redirect("/competitions")

        except Exception as e:
            return render_edit_form_with_error(competition_id, str(e))

    else:
        return render_edit_form_with_error(competition_id)


def render_edit_form_with_error(competition_id, error=None):
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Fetch dropdowns
        cur.execute("SELECT sportid, sportname FROM sport ")
        sports = cur.fetchall()
        cur.execute("SELECT refereeid, reffirstname, reflastname FROM referee ORDER BY reffirstname")
        referees = cur.fetchall()
        cur.execute("SELECT venueid, venuename FROM venue ORDER BY venuename")
        venues = cur.fetchall()
        cur.execute("SELECT tournamentid, tournamentyear, hostcountry FROM tournament ORDER BY tournamentyear DESC")
        tournaments = cur.fetchall()

        # Fetch competition details
        cur.execute("""
            SELECT competitionname, compdate, competitiontype, sportid,
                   refereeid, venueid, tournamentid
            FROM competition
            WHERE competitionid = %s
        """, (competition_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            return "תחרות לא נמצאה"

        competition = {
            "name": row[0],
            "date": row[1].strftime("%Y-%m-%d"),
            "type": row[2],
            "sportid": row[3],
            "refereeid": row[4],
            "venueid": row[5],
            "tournamentid": row[6]
        }

        return render_template("competition/edit_competition.html",
                               competition_id=competition_id,
                               competition=competition,
                               sports=sports,
                               referees=referees,
                               venues=venues,
                               tournaments=tournaments,
                               error=error)

    except Exception as e:
        return f"שגיאה בטעינת נתוני עריכת תחרות: {e}"



@competitions_bp.route("/delete/<int:competition_id>", methods=["POST"])
def delete_competition(competition_id):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM competition WHERE competitionid = %s", (competition_id,))
        conn.commit()
        cur.close()
        conn.close()

        return redirect("/competitions")

    except Exception as e:
        return f"שגיאה במחיקת תחרות: {e}"
