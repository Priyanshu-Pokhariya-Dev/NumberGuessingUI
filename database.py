from pymongo import MongoClient
from datetime import datetime

# ----------------- MONGODB CONNECTION -----------------
client = MongoClient("mongodb+srv://priyanshu:priyanshu1@project.i4fntrp.mongodb.net/?appName=project")
db = client["guess_game"]

best_scores = db["best_scores"]
history = db["history"]


# ------------------ SAVE SCORE ----------------------
def save_score(name, attempts):
    history.insert_one({
        "name": name,
        "attempts": attempts,
        "date": datetime.now()
    })

    existing = best_scores.find_one({"name": name})

    if existing:
        if attempts < existing["attempts"]:
            best_scores.update_one({"name": name}, {"$set": {"attempts": attempts}})
    else:
        best_scores.insert_one({"name": name, "attempts": attempts})


# ------------------ GET PLAYER HISTORY ----------------------
def get_history(name):
    return list(history.find({"name": name}).sort("date", -1))


# ------------------ GET LEADERBOARD ----------------------
def get_leaderboard():
    return best_scores.find().sort("attempts", 1)


def get_global_best():
    return best_scores.find_one(sort=[("attempts", 1)])
