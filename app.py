from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3

app = Flask(__name__)
# Hemmelig nøkkel for å sikre session-data
app.secret_key = "hemmelig_nøkkel"

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    # Oppretter brukertabell
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS brukere (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brukernavn TEXT,
            passord TEXT
        )
    """)
    conn.commit()
    conn.close()

# Registrering
@app.route("/registrer", methods=["GET", "POST"])
def registrer():
    if request.method == "POST":
        brukernavn = request.form["brukernavn"]
        passord = request.form["passord"]
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO brukere (brukernavn, passord) VALUES (?, ?)", (brukernavn, passord))
        conn.commit()
        conn.close()
        return redirect(url_for("logg_inn"))
    return render_template("registrer.html")

# Innlogging
@app.route("/logg_inn", methods=["GET", "POST"])
def logg_inn():
    if request.method == "POST":
        brukernavn = request.form["brukernavn"]
        passord = request.form["passord"]
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM brukere WHERE brukernavn=? AND passord=?", (brukernavn, passord))
        bruker = cursor.fetchone()
        conn.close()
        if bruker:
            # Lagrer brukernavn i session
            session["brukernavn"] = brukernavn
            return redirect(url_for("hjem"))
        else:
            return render_template("logg_inn.html", feil="Feil brukernavn eller passord")
    return render_template("logg_inn.html")

# Logg ut
@app.route("/logg_ut")
def logg_ut():
    session.pop("brukernavn", None)
    return redirect(url_for("logg_inn"))

@app.route("/")
def hjem():
    # Sjekker om brukeren er innlogget
    if "brukernavn" not in session:
        return redirect(url_for("logg_inn"))
    return render_template("index.html", brukernavn=session["brukernavn"])

if __name__ == "__main__":
    init_db()
    app.run(debug=True)