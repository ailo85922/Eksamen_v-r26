from flask import Flask, render_template, request
import random
import sqlite3

app = Flask(__name__)

# 🔧 INIT DATABASE
def init_db():
    conn = sqlite3.connect("game.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attempts INTEGER
        )
    """)

    conn.commit()
    conn.close()

init_db()

# 🎯 GAME STATE
number = random.randint(1, 100)
attempts = 0


@app.route("/", methods=["GET", "POST"])
def index():
    global number, attempts
    message = ""

    if request.method == "POST":
        guess = request.form.get("guess")

        # 🛡️ FEILHÅNDTERING (brukerstøtte)
        if not guess or not guess.isdigit():
            return render_template("index.html", message="Skriv et gyldig tall!")

        guess = int(guess)
        attempts += 1

        if guess < number:
            message = "For lavt"
        elif guess > number:
            message = "For høyt"
        else:
            message = f"Riktig! Du brukte {attempts} forsøk 🎉"

            # 💾 LAGRE TIL DATABASE
            conn = sqlite3.connect("game.db")
            c = conn.cursor()
            c.execute("INSERT INTO scores (attempts) VALUES (?)", (attempts,))
            conn.commit()
            conn.close()

            # 🔄 RESTART SPILL
            number = random.randint(1, 100)
            attempts = 0

    return render_template("index.html", message=message)


# 📊 VIS SCORE (valgfri ekstra)
@app.route("/scores")
def scores():
    conn = sqlite3.connect("game.db")
    c = conn.cursor()

    c.execute("SELECT * FROM scores ORDER BY id DESC")
    data = c.fetchall()

    conn.close()

    return {"scores": data}


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)