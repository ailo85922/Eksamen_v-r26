from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
import random

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
    # Oppretter leaderboard-tabell
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ledertavle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            navn TEXT,
            poeng INTEGER
        )
    """)
    conn.commit()
    conn.close()

# Hjemside – krever innlogging
@app.route("/")
def hjem():
    if "brukernavn" not in session:
        return redirect(url_for("logg_inn"))
    return render_template("index.html", brukernavn=session["brukernavn"])

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
    session.pop("tall", None)
    return redirect(url_for("logg_inn"))

# Gjett-spillet
@app.route("/gjett", methods=["GET", "POST"])
def gjett():
    if "brukernavn" not in session:
        return redirect(url_for("logg_inn"))
    if "tall" not in session:
        session["tall"] = random.randint(1, 100)
        session["forsok"] = 0  # Teller forsøk

    message = ""
    if request.method == "POST":
        session["forsok"] += 1  # Legger til ett forsøk
        guess = int(request.form["guess"])
        if guess < session["tall"]:
            message = "For lavt!"
        elif guess > session["tall"]:
            message = "For høyt!"
        else:
            poeng = max(100 - (session["forsok"] - 1) * 10, 10)  # Færre poeng per forsøk
            message = f"Riktig! 🎉 Du fikk {poeng} poeng!"
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO ledertavle (navn, poeng) VALUES (?, ?)",
                         (session["brukernavn"], poeng))
            conn.commit()
            conn.close()
            session.pop("tall", None)
            session.pop("forsok", None)

    return render_template("gjett.html", message=message)

# Leaderboard
@app.route("/ledertavle")
def ledertavle():
    if "brukernavn" not in session:
        return redirect(url_for("logg_inn"))
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    # Henter alle spillere sortert etter poeng
    cursor.execute("SELECT navn, poeng FROM ledertavle ORDER BY poeng DESC")
    spillere = cursor.fetchall()
    conn.close()
    return render_template("ledertavle.html", spillere=spillere)

# Lagre poeng til leaderboard
@app.route("/lagre", methods=["POST"])
def lagre():
    if "brukernavn" not in session:
        return redirect(url_for("logg_inn"))
    navn = session["brukernavn"]
    poeng = request.form["poeng"]
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ledertavle (navn, poeng) VALUES (?, ?)", (navn, poeng))
    conn.commit()
    conn.close()
    return redirect(url_for("ledertavle"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0")