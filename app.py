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

        session["player"] = player_name
        session["number"] = random.randint(1, 100)   # 🎲 Random magic number!
        session["attempts"] = 0                      # 🧮 Reset attempts

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
        try:
            guess = int(request.form["guess"])
        except:
            message = "⚠️ Please enter a valid number!"
            return render_template("game.html", message=message)

        session["attempts"] += 1
        number = session["number"]

        # 📏 How close is the guess?
        difference = abs(guess - number)

        # 🔮 HINT SYSTEM (Now extra spicy 🌶️🔥)
        if difference == 0:
            hint = ""
        elif difference <= 2:
            hint = "🔥 SUPER CLOSE! You're basically hugging the answer!"
        elif difference <= 5:
            hint = "✨ Very close! You can almost smell it!"
        elif difference <= 12:
            hint = "👍 Not bad, you're in the neighborhood!"
        elif difference <= 25:
            hint = "😐 Getting kinda far… Try again!"
        else:
            hint = "❄️ You’re in Antarctica… guess again!"

        # 📉📈 High / Low Feedback
        if guess < number:
            message = "⬇️ It's low!"
        elif guess > number:
            message = "⬆️ It's high!"
        else:
            result = f"🎉 Correct! ✨ You nailed it in {session['attempts']} attempts! 🏆"
            save_score(session["player"], session["attempts"])

        if hint:
            message = message + f"<br>💡 Hint: {hint}"

    # 📜 Player History
    player_history = get_history(session["player"])

    return render_template(
        "game.html",
        title="🎯 Play Game",
        player=session["player"],
        attempts=session["attempts"],
        message=message,
        result=result,
        history=player_history
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
        global_best=global_best
    )


# 🔄 ------------------ RESET GAME ----------------------
@app.route("/new_game")
def new_game():
    session.pop("number", None)
    session.pop("attempts", None)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
