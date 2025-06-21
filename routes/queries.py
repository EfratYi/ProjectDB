"""
@queries_bp.route("/run")
def run_queries():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM get_athletes_by_country(%s)", (2,))
    athletes = cur.fetchall()

    cur.execute("CALL delete_athletes_under_height(%s)", (150,))
    conn.commit()

    cur.close()
    conn.close()

    return render_template("advanced-operations.html", results=athletes)
"""