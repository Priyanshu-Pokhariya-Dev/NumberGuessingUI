from flask import Flask, render_template, request, redirect, session, url_for
import random
from database import save_score, get_history, get_leaderboard, get_global_best

app = Flask(__name__)
app.secret_key = "your_secret_key_here"


# 🎯 ------------------ HOME PAGE ----------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        player_name = request.form["name"].title()

        # Start a new game
        session["player"] = player_name
        session["number"] = random.randint(1, 100)
        session["attempts"] = 0
        session["guesses"] = []

        return redirect(url_for("game"))

    return render_template("index.html", title="🎮 Guess Game")


# 🕹️ ------------------ GAME PAGE ----------------------
@app.route("/game", methods=["GET", "POST"])
def game():
    if "player" not in session:
        return redirect("/")

    message = ""
    hint = ""
    result = None

    if request.method == "POST":
        guess_raw = request.form.get("guess", "").strip()

        try:
            guess = int(guess_raw)
        except ValueError:
            message = "⚠️ Please enter a valid number!"
        else:
            # Increase attempt count
            session["attempts"] = session.get("attempts", 0) + 1

            # 👉 Store this guess in the session list
            guesses = session.get("guesses", [])
            guesses.append(guess)
            session["guesses"] = guesses

            number = session["number"]

            # 📏 How close is the guess?
            difference = abs(guess - number)

            # 🔮 HINT SYSTEM
            if difference == 0:
                hint = ""
            elif difference <= 2:
                hint = "SUPER CLOSE!"
            elif difference <= 5:
                hint = "Very close!"
            elif difference <= 12:
                hint = "Not bad!"
            elif difference <= 25:
                hint = "Getting kinda far… Try again!"
            else:
                hint = "Way off! Try a very different number."

            # 📉📈 High / Low Feedback
            if guess < number:
                message = "⬇️ It's low!"
            elif guess > number:
                message = "⬆️ It's high!"
            else:
                result = f"🎉 Correct! ✨ You nailed it in {session['attempts']} attempts! 🏆"
                save_score(session["player"], session["attempts"])

            if hint and result is None:
                message = message + f"<br>💡 Hint: {hint}"

    # 📜 Player History from MongoDB
    player_history = get_history(session["player"])

    return render_template(
        "game.html",
        title="🎯 Play Game",
        player=session["player"],
        attempts=session.get("attempts", 0),
        message=message,
        result=result,
        history=player_history,
        guesses=session.get("guesses", []),
    )


# 🏆 ------------------ LEADERBOARD ----------------------
@app.route("/leaderboard")
def leaderboard():
    rankings = get_leaderboard()
    global_best = get_global_best()

    return render_template(
        "leaderboard.html",
        title="🏆 Leaderboard",
        rankings=rankings,
        global_best=global_best,
    )


# 🔄 ------------------ RESET GAME ----------------------
@app.route("/new_game")
def new_game():
    # keep player name, but reset the game completely
    if "player" not in session:
        return redirect("/")

    session["number"] = random.randint(1, 100)
    session["attempts"] = 0
    session["guesses"] = []

    return redirect(url_for("game"))


if __name__ == "__main__":
    app.run(debug=True)
