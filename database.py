from pymongo import MongoClient
from datetime import datetime

# ----------------- MONGODB CONNECTION -----------------
client = MongoClient("mongodb+srv://priyanshu:priyanshu1@project.7uihi2p.mongodb.net/?retryWrites=true&w=majority")
db = client["guess_game"]

best_scores = db["best_scores"]
history = db["history"]


def save_score(name, attempts):
    history.update_one(
        {"_id": name},
        {
            "$set": {
                "attempts": attempts,
                "date": datetime.now()
            }
        },
        upsert=True
    )

    existing = best_scores.find_one({"_id": name})

    if existing:
        if attempts < existing["attempts"]:
            best_scores.update_one(
                {"_id": name},
                {"$set": {"attempts": attempts}}
            )
    else:
        best_scores.insert_one({
            "_id": name,
            "attempts": attempts
        })



def get_history(name):
    return list(history.find({"_id": name}).sort("date", -1))


def get_leaderboard():
    return best_scores.find().sort("attempts", 1)


def get_global_best():
    return best_scores.find_one(sort=[("attempts", 1)])

