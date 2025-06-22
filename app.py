from flask import Flask, render_template
from routes.athletes import athletes_bp
from routes.sports import sports_bp
from routes.competition import competitions_bp
from routes.advanced_operations import advanced_ops_bp

app = Flask(__name__)

app.register_blueprint(athletes_bp)
app.register_blueprint(sports_bp)
app.register_blueprint(competitions_bp)
app.register_blueprint(advanced_ops_bp)

@app.route("/")
def main_menu():
    return render_template("main_menu.html")
if __name__ == "__main__":
    app.run(debug=True)