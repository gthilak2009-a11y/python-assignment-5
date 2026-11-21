import csv
import sqlite3
import pandas as pd
import time
import random
import cProfile

def generate_data(stations):
    filename = "air_quality.csv"

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["station", "date", "pm25"])

        for s in range(stations):
            for hour in range(8760):
                day = f"2026-{hour // 24 // 30 + 1:02d}-{hour // 24 % 30 + 1:02d}"

                writer.writerow([
                    f"Station{s+1}",
                    day,
                    random.randint(10, 150)
                ])

    return filename


# Method 1: Python loops
def python_loops(filename):
    data = {}

    with open(filename, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            key = (row["station"], row["date"])
            value = float(row["pm25"])

            if key not in data:
                data[key] = [0, 0]

            data[key][0] += value
            data[key][1] += 1

    return {
        key: total / count
        for key, (total, count) in data.items()
    }


# Method 2: Pandas
def pandas_method(filename):
    df = pd.read_csv(filename)

    return df.groupby(
        ["station", "date"]
    )["pm25"].mean()


# Method 3: SQL
def sql_method(filename):
    con = sqlite3.connect(":memory:")

    con.execute("""
    CREATE TABLE aq (
        station TEXT,
        day TEXT,
        pm25 REAL
    )
    """)

    with open(filename, "r") as file:
        reader = csv.DictReader(file)

        rows = [
            (r["station"], r["date"], float(r["pm25"]))
            for r in reader
        ]

    con.executemany(
        "INSERT INTO aq VALUES (?, ?, ?)", rows
    )

    result = con.execute("""
        SELECT station, day, AVG(pm25)
        FROM aq
        GROUP BY station, day
    """).fetchall()

    con.close()

    return result


# Compare execution times
for stations in [1, 12, 120]:

    print("\nStations:", stations)

    filename = generate_data(stations)

    start = time.perf_counter()
    result1 = python_loops(filename)
    print("Python Loops:", time.perf_counter() - start)

    start = time.perf_counter()
    result2 = pandas_method(filename)
    print("Pandas:", time.perf_counter() - start)

    start = time.perf_counter()
    result3 = sql_method(filename)
    print("SQL:", time.perf_counter() - start)

    print("Results calculated:", len(result1))

# Profile Python loops
print("\nProfiling Python Loops:")
cProfile.run(
    "python_loops('air_quality.csv')"
)
