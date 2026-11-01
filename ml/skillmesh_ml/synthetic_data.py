"""Synthetic students with hidden ground truth. Used for testing, evaluation and seeding the database."""
import csv
import random

CANON = {
    "python": ["python", "python programming", "py scripting"],
    "javascript": ["javascript", "js", "javascript basics"],
    "react": ["react", "reactjs", "react frontend"],
    "sql": ["sql", "sql databases", "postgres queries"],
    "machine learning": ["machine learning", "ml", "scikit-learn modeling"],
    "data analysis": ["data analysis", "excel analytics", "pandas analysis"],
    "ui design": ["ui design", "figma", "ui/ux design"],
    "photoshop": ["photoshop", "photo editing"],
    "video editing": ["video editing", "premiere pro"],
    "guitar": ["guitar", "acoustic guitar"],
    "public speaking": ["public speaking", "presentation skills"],
    "c++": ["c++", "cpp programming"],
    "java": ["java", "core java"],
    "dsa": ["data structures", "dsa", "algorithms"],
    "content writing": ["content writing", "blog writing"],
    "french": ["french", "french language"],
    "digital marketing": ["digital marketing", "seo basics"],
    "git": ["git", "git and github"],
    "fastapi": ["fastapi", "python rest apis"],
    "arduino": ["arduino", "embedded basics"],
}
ALL_PHRASES = [p for variants in CANON.values() for p in variants]
FIRST = ["Aarav", "Ananya", "Kabir", "Meera", "Rohan", "Isha", "Arjun", "Diya", "Vihaan", "Sanya", "Karan", "Nisha",
         "Yash", "Pooja", "Aditya", "Riya", "Manav", "Tanvi", "Harsh", "Kavya", "Dev", "Simran", "Nikhil", "Aisha"]
LAST = ["Sharma", "Verma", "Rathore", "Mehta", "Gupta", "Joshi", "Singh", "Agarwal", "Bhatt", "Chauhan", "Jain", "Saini"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def generate_users(count: int = 48, seed: int = 2024) -> list[dict]:
    rnd = random.Random(seed)
    users = []
    for i in range(count):
        offered_ids = rnd.sample(list(CANON), rnd.choice([2, 3]))
        wanted_ids = rnd.sample([c for c in CANON if c not in offered_ids], rnd.choice([2, 3]))
        slots = [f"{d}-{s}" for d in DAYS for s in "MAE" if rnd.random() < 0.3]
        users.append({
            "id": f"u{i + 1:02d}",
            "name": f"{FIRST[i % len(FIRST)]} {rnd.choice(LAST)}",
            "experience": rnd.randint(1, 5),
            "offered_ids": offered_ids, "wanted_ids": wanted_ids,
            "offered": [rnd.choice(CANON[c]) for c in offered_ids],
            "wanted": [rnd.choice(CANON[c]) for c in wanted_ids],
            "availability": slots,
            "rating": round(3 + rnd.random() * 2, 1),
            "rating_count": rnd.randint(3, 17),
        })
    return users


def write_csv(path: str, users: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "name", "experience", "offered", "wanted", "availability", "rating"])
        for u in users:
            w.writerow([u["id"], u["name"], u["experience"], "|".join(u["offered"]), "|".join(u["wanted"]),
                        "|".join(u["availability"]), u["rating"]])
