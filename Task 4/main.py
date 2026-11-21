import re
import sqlite3
import time
from collections import Counter

POSITIVE = {
    "good", "clean", "fast", "helpful", "improved"
}

NEGATIVE = {
    "bad", "dirty", "slow", "rude", "smoke", "broken"
}

NEGATORS = {"not", "never", "no"}


# Sentiment Analysis
def score(text):
    words = re.findall(r"\b\w+\b", text.lower())

    total = 0

    for i, word in enumerate(words):
        value = 1 if word in POSITIVE else -1 if word in NEGATIVE else 0

        if i > 0 and words[i - 1] in NEGATORS:
            value = -value

        total += value

    return total


def label(text):
    s = score(text)

    if s > 0:
        return "positive"
    elif s < 0:
        return "negative"
    else:
        return "neutral"


# Text Summarisation
def summarise(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)

    words = re.findall(r"\b\w+\b", text.lower())

    stopwords = {
        "the", "is", "and", "a", "are", "was",
        "in", "from", "to", "of", "it", "this"
    }

    frequency = Counter(
        word for word in words if word not in stopwords
    )

    if not sentences:
        return ""

    best_sentence = max(
        sentences,
        key=lambda sentence: sum(
            frequency[word]
            for word in re.findall(r"\b\w+\b", sentence.lower())
        )
    )

    return best_sentence


# 50 Citizen Complaints
complaints = [
    "The roads are clean and buses are fast.",
    "Smoke is bad and air is dirty.",
    "The staff are not helpful.",
    "Air quality has improved.",
    "The factory produces smoke and pollution.",
    "The roads are dirty and broken.",
    "The service is good and helpful.",
    "The buses are slow.",
    "The air is clean and good.",
    "The staff are rude and unhelpful."
] * 5


# Display Sentiment Results
print("SENTIMENT ANALYSIS")

for complaint in complaints:
    print(label(complaint), "|", complaint)


# Text Summarisation
print("\nTEXT SUMMARISATION")

text = " ".join(complaints)

print(summarise(text))


# Agreement with manually assigned labels
actual_labels = [
    "positive", "negative", "negative", "positive",
    "negative", "negative", "positive", "negative",
    "positive", "negative"
] * 5

correct = 0

for complaint, actual in zip(complaints, actual_labels):
    if label(complaint) == actual:
        correct += 1

print("\nLABEL AGREEMENT")
print("Correct:", correct, "out of", len(complaints))
print("Agreement:", round(correct / len(complaints) * 100, 2), "%")


# SQLite Database
con = sqlite3.connect(":memory:")

con.execute("""
CREATE TABLE aq (
    station TEXT,
    day TEXT,
    pm25 REAL
)
""")

data = [
    ("Adyar", "2026-10-01", 48),
    ("Guindy", "2026-10-01", 95),
    ("Adyar", "2026-10-02", 60),
    ("Guindy", "2026-10-02", 121)
]

con.executemany(
    "INSERT INTO aq VALUES (?, ?, ?)", data
)

# Measure query before indexing
start = time.perf_counter()

for i in range(1000):
    con.execute(
        "SELECT AVG(pm25) FROM aq WHERE station=? AND day=?",
        ("Adyar", "2026-10-01")
    ).fetchone()

before = time.perf_counter() - start

# Create index
con.execute(
    "CREATE INDEX idx_station_day ON aq(station, day)"
)

# Measure query after indexing
start = time.perf_counter()

for i in range(1000):
    con.execute(
        "SELECT AVG(pm25) FROM aq WHERE station=? AND day=?",
        ("Adyar", "2026-10-01")
    ).fetchone()

after = time.perf_counter() - start

print("\nDATABASE INDEXING")
print("Before Index:", before)
print("After Index:", after)

con.close()
