from flask import Blueprint, request, render_template, jsonify
from db import get_connection
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

advanced_ops_bp = Blueprint('advanced_ops_bp', __name__, url_prefix='/advanced-operations')

@advanced_ops_bp.route("/")
def advanced_operations():
    print("Advanced Operations route accessed")
    try:
        return render_template("advanced_operations/advanced-operations.html")
    except Exception as e:
        return f"שגיאה בטעינת מסך פעולות מתקדמות: {e}", 500

@advanced_ops_bp.route("/api/query1", methods=["GET"])
def run_query1():
    try:
        conn = get_connection()
        cur = conn.cursor()
        logger.debug("Executing query 1")
        cur.execute("""
            WITH RankedMedals AS (
                SELECT 
                    a.AthleteID,
                    a.AthleteName, 
                    a.Gender, 
                    c.CountryName,
                    DATE_PART('year', AGE(CURRENT_DATE, a.Birthday)) AS Age,
                    MAX(CASE 
                        WHEN r.Medal = 'Gold' THEN 3
                        WHEN r.Medal = 'Silver' THEN 2
                        WHEN r.Medal = 'Bronze' THEN 1
                        END) AS BestMedalScore
                FROM Athlete a
                JOIN AthleteCompetition r ON a.AthleteID = r.AthleteID
                JOIN Country c ON a.CountryId = c.CountryId
                WHERE EXTRACT(YEAR FROM a.Birthday) > 2000 AND r.Medal IS NOT NULL
                GROUP BY a.AthleteID, a.AthleteName, a.Gender, c.CountryName, a.Birthday
            )
            SELECT 
                AthleteName, 
                Gender, 
                CountryName,
                Age,
                CASE BestMedalScore
                    WHEN 3 THEN 'Gold'
                    WHEN 2 THEN 'Silver'
                    WHEN 1 THEN 'Bronze'
                END AS BestMedal
            FROM RankedMedals
            ORDER BY CountryName ASC;
        """)
        rows = cur.fetchall()
        logger.debug(f"Query 1 fetched {len(rows)} rows")
        cur.close()
        conn.close()

        result = [
            {
                "AthleteName": row[0],
                "Gender": row[1],
                "CountryName": row[2],
                "Age": row[3],
                "BestMedal": row[4]
            }
            for row in rows
        ]
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in query1: {str(e)}", exc_info=True)
        return jsonify({"error": f"שגיאה בביצוע שאילתה 1: {str(e)}"}), 500

@advanced_ops_bp.route("/api/query2", methods=["GET"])
def run_query2():
    try:
        conn = get_connection()
        cur = conn.cursor()
        logger.debug("Executing query 2")
        cur.execute("""
            SELECT 
                s.SportName, 
                COUNT(co.CompetitionId) AS NumCompetitions, 
                COUNT(DISTINCT v.VenueName) AS NumVenues,
                COUNT(r.Medal) AS NumMedals,
                MIN(co.CompDate) AS EarliestCompetitionDate
            FROM Sport s
            LEFT JOIN Competition co ON s.SportID = co.SportID
            LEFT JOIN Venue v ON co.VenueID = v.VenueID 
            LEFT JOIN AthleteCompetition r ON co.CompetitionId = r.CompetitionId
            GROUP BY s.SportName
            ORDER BY s.SportName, MIN(co.CompDate);
        """)
        rows = cur.fetchall()
        logger.debug(f"Query 2 fetched {len(rows)} rows")
        cur.close()
        conn.close()

        result = [
            {
                "SportName": row[0],
                "NumCompetitions": row[1],
                "NumVenues": row[2],
                "NumMedals": row[3],
                "EarliestCompetitionDate": row[4].strftime("%Y-%m-%d") if row[4] else None
            }
            for row in rows
        ]
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in query2: {str(e)}", exc_info=True)
        return jsonify({"error": f"שגיאה בביצוע שאילתה 2: {str(e)}"}), 500

from flask import request, jsonify

@advanced_ops_bp.route("/api/function1", methods=["GET"])
def run_function1():
    try:
        country_id = request.args.get("countryId")
        if not country_id:
            return jsonify({"error": "חובה לספק מזהה מדינה"}), 400

        conn = get_connection()
        cur = conn.cursor()

        # קוראים לפונקציה שמחזירה טבלה
        cur.execute("SELECT * FROM get_top_athletes_by_country(%s);", (int(country_id),))
        rows = cur.fetchall()

        cur.close()
        conn.close()

        result = [
            {"athletename": row[0], "total_medals": row[1]}
            for row in rows
        ]
        return jsonify(result)

    except Exception as e:
        logger.error(f"Error in function1: {str(e)}", exc_info=True)
        return jsonify({"error": f"שגיאה בביצוע פונקציה 1: {str(e)}"}), 500


@advanced_ops_bp.route("/api/function2", methods=["GET"])
def run_function2():
    try:
        team_id = request.args.get("teamId")
        if not team_id:
            return jsonify({"error": "חובה לספק מזהה קבוצה"}), 400

        conn = get_connection()
        cur = conn.cursor()
        logger.debug(f"Executing function2 with team_id={team_id}")
        cur.execute("SELECT calculate_average_team_score(%s)", (int(team_id),))
        avg_score = cur.fetchone()[0]
        cur.close()
        conn.close()

        return jsonify({"avg_score": float(avg_score)})

    except Exception as e:
        logger.error(f"Error in function2: {str(e)}", exc_info=True)
        return jsonify({"error": f"שגיאה בביצוע פונקציה 2: {str(e)}"}), 500

@advanced_ops_bp.route("/api/procedure1", methods=["POST"])
def run_procedure1():
    try:
        conn = get_connection()
        cur = conn.cursor()
        logger.debug("Executing procedure1")
        cur.execute("CALL assign_random_referees_to_unassigned_competitions();")
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "שיוך שופטים אקראיים בוצע בהצלחה"})

    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        logger.error(f"Error in procedure1: {str(e)}", exc_info=True)
        return jsonify({"error": f"שגיאה בביצוע פרוצדורה 1: {str(e)}"}), 500

@advanced_ops_bp.route("/api/procedure2", methods=["POST"])
def run_procedure2():
    try:
        conn = get_connection()
        cur = conn.cursor()
        logger.debug("Executing procedure2")
        cur.execute("CALL update_medal_count_by_country();")
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "עדכון ספירת מדליות לפי מדינה בוצע בהצלחה"})

    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        logger.error(f"Error in procedure2: {str(e)}", exc_info=True)
        return jsonify({"error": f"שגיאה בביצוע פרוצדורה 2: {str(e)}"}), 500